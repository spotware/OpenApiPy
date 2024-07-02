import asyncio
from collections import deque
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import ProtoMessage, ProtoHeartbeatEvent
import datetime


class TcpProtocol(asyncio.Protocol):
    MAX_LENGTH = 15000000
    _send_queue = deque([])
    _send_task = None
    _lastSendMessageTime = None

    def connection_made(self, transport):
        self.transport = transport

        if not self._send_task:
            self._send_task = asyncio.create_task(self._send_strings())
        self.factory.connected(self)

    def connection_lost(self, exc):
        if self._send_task:
            self._send_task.cancel()
        self.factory.disconnected(exc)

    def heartbeat(self):
        self.send(ProtoHeartbeatEvent(), True)

    def send(self, message, instant=False, clientMsgId=None, isCanceled = None):
        data = b''

        if isinstance(message, ProtoMessage):
            data = message.SerializeToString()

        if isinstance(message, bytes):
            data = message

        if isinstance(message, ProtoMessage.__base__):
            msg = ProtoMessage(payload=message.SerializeToString(),
                               clientMsgId=clientMsgId,
                               payloadType=message.payloadType)
            data = msg.SerializeToString()

        if instant:
            self.transport.write(data)
            self._lastSendMessageTime = datetime.datetime.now()
        else:
            self._send_queue.append((isCanceled, data))

    async def _send_strings(self):
        while True:
            await asyncio.sleep(1)
            size = len(self._send_queue)

            if not size:
                if self._lastSendMessageTime is None or (datetime.datetime.now() - self._lastSendMessageTime).total_seconds() > 20:
                    self.heartbeat()
                continue

            for _ in range(min(size, self.factory.numberOfMessagesToSendPerSecond)):
                isCanceled, data = self._send_queue.popleft()
                if isCanceled is not None and isCanceled():
                    continue
                self.transport.write(data)
            self._lastSendMessageTime = datetime.datetime.now()

    def data_received(self, data):
        msg = ProtoMessage()
        msg.ParseFromString(data)

        if msg.payloadType == ProtoHeartbeatEvent().payloadType:
            self.heartbeat()
        self.factory.received(msg)
        return data
