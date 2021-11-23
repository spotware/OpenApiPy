import sys
from collections import deque
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet import task
from messages.OpenApiCommonModelMessages_pb2 import *
from messages.OpenApiCommonMessages_pb2 import *
from messages.OpenApiMessages_pb2 import *
from messages.OpenApiModelMessages_pb2 import *

class Protocol(Int32StringReceiver):

    MAX_LENGTH = sys.maxsize // 2

    _rps_limit = 5
    _send_queue = deque([])
    _send_task_interval = 1
    _send_task = None

    def connectionMade(self):
        super().connectionMade()

        if not self._send_task:
            self._send_task = task.LoopingCall(self._sendStrings)
        self._send_task.start(self._send_task_interval)

    def connectionLost(self, reason):
        super().connectionLost(reason)
        if self._send_task.running:
            self._send_task.stop()

    def heartbeat(self):
        self.send(ProtoHeartbeatEvent(), True)

    def send(self, message, instant=False, msgid=None):
        data = b''

        if isinstance(message, ProtoMessage):
            data = message.SerializeToString()

        if isinstance(message, bytes):
            data = message

        if isinstance(message, ProtoMessage.__base__):
            msg = ProtoMessage(payload=message.SerializeToString(),
                               clientMsgId=msgid,
                               payloadType=message.payloadType)
            data = msg.SerializeToString()

        if instant:
            self.sendString(data)
        else:
            self._send_queue.append(data)

    def _sendStrings(self):
        size = len(self._send_queue)

        if not size:
            return  # pragma: no cover

        for _ in range(min(size, self._rps_limit)):
            self.sendString(self._send_queue.popleft())

    def stringReceived(self, data):
        msg = ProtoMessage()
        msg.ParseFromString(data)

        if msg.payloadType == ProtoHeartbeatEvent().payloadType:
            self.heartbeat()

        self.receive(msg)
        return data

    def receive(self, message):
        pass  # pragma: no cover