#!/usr/bin/env python
"""
Modern cTrader Open API Client using WebSocket and asyncio.
Replaces the Twisted-based implementation with a more developer-friendly approach.
"""

import asyncio
import logging
import ssl
import struct
import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Callable, Awaitable, Any
from datetime import datetime, timedelta

from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoMessage, ProtoHeartbeatEvent
from ctrader_open_api.protobuf import Protobuf


logger = logging.getLogger(__name__)


class ModernClient:
    """
    Modern cTrader Open API Client using raw TCP and asyncio.

    Features:
    - Async/await interface instead of Twisted deferreds
    - Raw TCP connection with SSL (cTrader compatible)
    - Built-in rate limiting and message queuing
    - Automatic heartbeat handling
    - Event-driven message handling
    - Connection retry logic
    - Type hints throughout
    """

    def __init__(
        self,
        host: str,
        port: int = 5035,
        max_messages_per_second: int = 5,
        connection_timeout: int = 30,
        response_timeout: int = 15,
        max_reconnect_attempts: int = 5,
        reconnect_delay: int = 5
    ):
        """
        Initialize the modern client.

        Args:
            host: Host address (e.g., "demo.ctraderapi.com")
            port: Port number (default: 5035)
            max_messages_per_second: Rate limit for outgoing messages
            connection_timeout: Connection timeout in seconds
            response_timeout: Default response timeout for requests
            max_reconnect_attempts: Maximum reconnection attempts
            reconnect_delay: Delay between reconnection attempts
        """
        self.host = host
        self.port = port
        self.max_messages_per_second = max_messages_per_second
        self.connection_timeout = connection_timeout
        self.response_timeout = response_timeout
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay

        # Connection state
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.is_connected = False
        self.reconnect_count = 0

        # Message handling
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_queue: deque = deque()
        self.last_message_time: Optional[datetime] = None

        # Event handlers
        self.message_handlers: Dict[int, List[Callable]] = defaultdict(list)
        self.connection_callbacks: List[Callable] = []
        self.disconnection_callbacks: List[Callable] = []

        # Background tasks
        self._sender_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._receiver_task: Optional[asyncio.Task] = None

        # Setup logging
        logging.basicConfig(level=logging.INFO)

    async def connect(self) -> bool:
        """
        Connect to the cTrader server using raw TCP with SSL.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create SSL context for secure connection
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False  # cTrader uses custom certificates
            ssl_context.verify_mode = ssl.CERT_NONE

            logger.info(f"Connecting to {self.host}:{self.port}")

            # Use raw TCP connection for cTrader compatibility
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port, ssl=ssl_context),
                timeout=self.connection_timeout
            )

            self.reader = reader
            self.writer = writer
            self.is_connected = True
            self.reconnect_count = 0

            logger.info(f"Connected to {self.host}:{self.port}")

            # Start background tasks
            await self._start_background_tasks()

            # Notify connection callbacks
            for callback in self.connection_callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self)
                else:
                    callback(self)

            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the server."""
        if self.is_connected:
            self.is_connected = False

            # Stop background tasks
            await self._stop_background_tasks()

            # Close connection
            if hasattr(self, 'writer'):
                self.writer.close()
                await self.writer.wait_closed()

            # Notify disconnection callbacks
            for callback in self.disconnection_callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self, "Manual disconnect")
                else:
                    callback(self, "Manual disconnect")

            logger.info("Disconnected from server")

    async def send_message(
        self,
        message,
        client_msg_id: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Any:
        """
        Send a message and wait for response.

        Args:
            message: Protobuf message to send
            client_msg_id: Optional client message ID
            timeout: Response timeout (uses default if None)

        Returns:
            Response message or None if timeout
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to server")

        # Generate client message ID if not provided
        if client_msg_id is None:
            client_msg_id = str(int(time.time() * 1000000))

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[client_msg_id] = future

        try:
            # Queue the message for sending
            self._queue_message(message, client_msg_id)

            # Wait for response with timeout
            timeout = timeout or self.response_timeout
            response = await asyncio.wait_for(future, timeout=timeout)

            return response

        except asyncio.TimeoutError:
            logger.error(f"Request timeout for message {client_msg_id}")
            return None
        finally:
            # Cleanup
            self.pending_requests.pop(client_msg_id, None)

    def send_message_no_response(self, message, client_msg_id: Optional[str] = None):
        """
        Send a message without waiting for response (fire and forget).

        Args:
            message: Protobuf message to send
            client_msg_id: Optional client message ID
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to server")

        if client_msg_id is None:
            client_msg_id = str(int(time.time() * 1000000))

        self._queue_message(message, client_msg_id)

    def _queue_message(self, message, client_msg_id: str):
        """Queue a message for sending with rate limiting."""
        # Serialize the message
        if hasattr(message, 'SerializeToString'):
            # Wrap in ProtoMessage container
            proto_msg = ProtoMessage(
                payload=message.SerializeToString(),
                clientMsgId=client_msg_id,
                payloadType=message.payloadType
            )
            data = proto_msg.SerializeToString()
        else:
            data = message

        self.message_queue.append((data, client_msg_id))

    async def _start_background_tasks(self):
        """Start background tasks for message handling."""
        self._sender_task = asyncio.create_task(self._message_sender())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_manager())
        self._receiver_task = asyncio.create_task(self._message_receiver())

    async def _stop_background_tasks(self):
        """Stop all background tasks."""
        tasks = [self._sender_task, self._heartbeat_task, self._receiver_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def _message_sender(self):
        """Background task to send queued messages with rate limiting."""
        try:
            while self.is_connected:
                await asyncio.sleep(1.0)  # Check every second

                if not self.message_queue:
                    continue

                # Send up to max_messages_per_second messages
                messages_sent = 0
                while (self.message_queue and
                       messages_sent < self.max_messages_per_second):

                    data, client_msg_id = self.message_queue.popleft()
                    await self._send_raw_data(data)
                    messages_sent += 1
                    self.last_message_time = datetime.now()

        except asyncio.CancelledError:
            logger.debug("Message sender task cancelled")
        except Exception as e:
            logger.error(f"Error in message sender: {e}")

    async def _send_raw_data(self, data: bytes):
        """Send raw data over TCP connection."""
        try:
            # Send length prefix (4 bytes, big-endian) followed by data
            length = len(data)
            length_bytes = struct.pack('>I', length)

            self.writer.write(length_bytes + data)
            await self.writer.drain()

        except Exception as e:
            logger.error(f"Failed to send data: {e}")
            await self._handle_connection_error()

    async def _message_receiver(self):
        """Background task to receive and process messages."""
        try:
            while self.is_connected:
                # Read message length (4 bytes)
                length_data = await self.reader.readexactly(4)
                length = struct.unpack('>I', length_data)[0]

                # Read message data
                message_data = await self.reader.readexactly(length)

                # Parse protobuf message
                proto_msg = ProtoMessage()
                proto_msg.ParseFromString(message_data)

                await self._handle_received_message(proto_msg)

        except asyncio.CancelledError:
            logger.debug("Message receiver task cancelled")
        except Exception as e:
            logger.error(f"Error in message receiver: {e}")
            await self._handle_connection_error()

    async def _handle_received_message(self, message: ProtoMessage):
        """Handle a received message."""
        # Handle heartbeat
        if message.payloadType == ProtoHeartbeatEvent().payloadType:
            await self._send_heartbeat()
            return

        # Handle pending request responses
        if message.clientMsgId and message.clientMsgId in self.pending_requests:
            future = self.pending_requests[message.clientMsgId]
            if not future.cancelled():
                future.set_result(message)
            return

        # Handle event messages (broadcast to handlers)
        handlers = self.message_handlers.get(message.payloadType, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")

    async def _heartbeat_manager(self):
        """Background task to manage heartbeat."""
        try:
            while self.is_connected:
                await asyncio.sleep(20)  # Send heartbeat every 20 seconds

                # Check if we need to send heartbeat
                if (self.last_message_time is None or
                    (datetime.now() - self.last_message_time).total_seconds() > 20):
                    await self._send_heartbeat()

        except asyncio.CancelledError:
            logger.debug("Heartbeat task cancelled")
        except Exception as e:
            logger.error(f"Error in heartbeat manager: {e}")

    async def _send_heartbeat(self):
        """Send heartbeat message."""
        heartbeat = ProtoHeartbeatEvent()
        heartbeat_msg = ProtoMessage(
            payload=heartbeat.SerializeToString(),
            payloadType=heartbeat.payloadType
        )
        data = heartbeat_msg.SerializeToString()
        await self._send_raw_data(data)
        self.last_message_time = datetime.now()

    async def _handle_connection_error(self):
        """Handle connection errors and attempt reconnection."""
        if not self.is_connected:
            return

        self.is_connected = False
        logger.warning("Connection lost, attempting to reconnect...")

        # Stop background tasks
        await self._stop_background_tasks()

        # Notify disconnection callbacks
        for callback in self.disconnection_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self, "Connection error")
                else:
                    callback(self, "Connection error")
            except Exception as e:
                logger.error(f"Error in disconnection callback: {e}")

        # Attempt reconnection
        await self._attempt_reconnection()

    async def _attempt_reconnection(self):
        """Attempt to reconnect with exponential backoff."""
        while (self.reconnect_count < self.max_reconnect_attempts and
               not self.is_connected):

            self.reconnect_count += 1
            delay = self.reconnect_delay * (2 ** (self.reconnect_count - 1))

            logger.info(f"Reconnection attempt {self.reconnect_count}/{self.max_reconnect_attempts} "
                       f"in {delay} seconds...")

            await asyncio.sleep(delay)

            if await self.connect():
                logger.info("Reconnection successful")
                return

        logger.error("Max reconnection attempts reached")

    def add_message_handler(self, payload_type: int, handler: Callable):
        """
        Add a message handler for a specific payload type.

        Args:
            payload_type: Message payload type to handle
            handler: Handler function (can be async)
        """
        self.message_handlers[payload_type].append(handler)

    def remove_message_handler(self, payload_type: int, handler: Callable):
        """Remove a message handler."""
        if payload_type in self.message_handlers:
            try:
                self.message_handlers[payload_type].remove(handler)
            except ValueError:
                pass

    def add_connection_callback(self, callback: Callable):
        """Add a callback for connection events."""
        self.connection_callbacks.append(callback)

    def add_disconnection_callback(self, callback: Callable):
        """Add a callback for disconnection events."""
        self.disconnection_callbacks.append(callback)


class ClientError(Exception):
    """Base exception for client errors."""
    pass


class ConnectionError(ClientError):
    """Exception raised for connection-related errors."""
    pass


class TimeoutError(ClientError):
    """Exception raised for timeout errors."""
    pass