#!/usr/bin/env python

import calendar
import asyncio
import datetime
import time
from collections import deque
from inputimeout import inputimeout, TimeoutOccurred
from ctrader_open_api.endpoints import EndPoints
from ctrader_open_api.protobuf import Protobuf
from ctrader_open_api.messages.OpenApiCommonMessages_pb2 import *
from ctrader_open_api.messages.OpenApiMessages_pb2 import *
from ctrader_open_api.messages.OpenApiModelMessages_pb2 import *


import tracemalloc
tracemalloc.start()


class TcpProtocol(asyncio.Protocol):
    MAX_LENGTH = 15000000

    def __init__(self, client):
        print('$TcpProtocol __init__')
        self.client = client
        self.transport = None
        self._send_queue = deque([])
        self._send_task = None
        self._last_send_message_time = None

    def connection_made(self, transport):
        global time_now
        time_now = datetime.datetime.now()
        print('$TcpProtocol connection_made')

        self.transport = transport
        if self._send_task is None:
            self._send_task = asyncio.create_task(self._send_strings())
        asyncio.create_task(self.client.connected(self))

    def connection_lost(self, exc):
        print('$TcpProtocol connection_lost')

        print(datetime.datetime.now() - time_now)

        if self._send_task:
            self._send_task.cancel()
        print(f'connection lost: {exc}')
        asyncio.create_task(self.client.disconnected(exc))

    def heartbeat(self):
        print('$TcpProtocol heartbeat')
        self.send(ProtoHeartbeatEvent(), True)

    def send(self, message, instant=False, clientMsgId=None, is_canceled=None):
        print('$TcpProtocol send')

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

        print(f'protocol _send data: {data}')

        if instant:
            self.transport.write(data)
            self._last_send_message_time = datetime.datetime.now()
        else:
            self._send_queue.append((is_canceled, data))

    async def _send_strings(self):

        while True:
            print('$TcpProtocol _send_strings')
            if not self._send_queue:
                if self._last_send_message_time is None or (
                    datetime.datetime.now() - self._last_send_message_time).total_seconds() > 20:
                    self.heartbeat()
                await asyncio.sleep(2)
                continue

            for _ in range(min(len(self._send_queue), self.client.number_of_messages_to_send_per_second)):
                is_canceled, data = self._send_queue.popleft()
                if is_canceled is not None and is_canceled():
                    continue
                self.transport.write(data)
            self._last_send_message_time = datetime.datetime.now()
            await asyncio.sleep(2)

    def data_received(self, data):
        print('$TcpProtocol data_received')

        msg = ProtoMessage()
        msg.ParseFromString(data)

        if msg.payloadType == ProtoHeartbeatEvent().payloadType:
            self.heartbeat()

        asyncio.create_task(self.client.received(msg))


class Client:
    def __init__(self, host, port, protocol_factory, number_of_messages_to_send_per_second=5):
        print('*Client __init__')
        self.host = host
        self.port = port
        self.protocol: TcpProtocol = None
        self.protocol_factory = protocol_factory
        self.number_of_messages_to_send_per_second = number_of_messages_to_send_per_second
        self._events = dict()
        self._response_deferreds = dict()
        self.is_connected = False
        self._loop = asyncio.get_event_loop()

    async def start(self):
        print('*Client start')
        transport, protocol = await self._loop.create_connection(
            lambda: self.protocol_factory(self),
            self.host, self.port
        )
        self.transport = transport
        self.protocol = protocol

        await self._loop.create_task(asyncio.sleep(5))

    async def connected(self, protocol):
        print('*Client connected')
        self.is_connected = True
        if hasattr(self, "_connected_callback"):
            await self._connected_callback(self)

    async def disconnected(self, reason):
        print('*Client disconnected')
        print('DISCONNECTED!!! ')
        self.is_connected = False
        self._response_deferreds.clear()
        if hasattr(self, "_disconnected_callback"):
            await self._disconnected_callback(self, reason)

    async def received(self, message):
        print('*Client received')

        if hasattr(self, "_message_received_callback"):
            await self._message_received_callback(self, message)
        if (message.clientMsgId is not None and message.clientMsgId in self._response_deferreds):
            response_deferred: asyncio.Future = self._response_deferreds[message.clientMsgId]

            self._response_deferreds.pop(message.clientMsgId)
            response_deferred.set_result(message)

    async def _send_message(self, message, clientMsgId):
        print('*Client _send_message')
        self.protocol.send(message, clientMsgId=clientMsgId, is_canceled=lambda: clientMsgId not in self._response_deferreds)
        self._response_deferreds[clientMsgId].set_result("Message sent successfully")

    async def send(self, message, clientMsgId=None, response_timeout_in_seconds=50, **params):
        print('*Client send')
        if type(message) in [str, int]:
            message = Protobuf.get(message, **params)
        response_future = self._loop.create_future()
        if clientMsgId is None:
            clientMsgId = str(id(response_future))
        if clientMsgId is not None:
            self._response_deferreds[clientMsgId] = response_future

        await asyncio.sleep(1)

        try:

            await self._send_message(message, clientMsgId=clientMsgId)

            if response_future.done():
                response = response_future.result()
            else:
                response = await asyncio.wait_for(response_future, timeout=response_timeout_in_seconds)

        except asyncio.TimeoutError:
            self._on_response_failure(clientMsgId)
            print(f'TimeoutError: {response}')
            raise
        finally:
            self._response_deferreds.pop(clientMsgId, None)

        return response

    def _on_response_failure(self, clientMsgId):
        print('*Client _on_response_failure')
        if clientMsgId in self._response_futures:
            future = self._response_futures.pop(clientMsgId)
            future.set_exception(asyncio.TimeoutError())

    def setConnectedCallback(self, callback):
        print('*Client setConnectedCallback')
        self._connected_callback = callback

    def setDisconnectedCallback(self, callback):
        print('*Client setDisconnectedCallback')
        self._disconnected_callback = callback

    def setMessageReceivedCallback(self, callback):
        print('*Client setMessageReceivedCallback')
        self._message_received_callback = callback


async def main():
    currentAccountId = None

    hostType = input("Host (Live/Demo): ")
    hostType = hostType.lower()

    while hostType != "live" and  hostType != "demo":
        print(f"{hostType} is not a valid host type.")
        hostType = input("Host (Live/Demo): ")

    appClientId = input("App Client ID: ")
    appClientSecret = input("App Client Secret: ")
    isTokenAvailable = input("Do you have an access token? (Y/N): ").lower() == "y"

    accessToken = None
    if isTokenAvailable == False:
        appRedirectUri = input("App Redirect URI: ")
        auth = Auth(appClientId, appClientSecret, appRedirectUri)
        authUri = auth.getAuthUri()
        print(f"Please continue the authentication on your browser:\n {authUri}")
        webbrowser.open_new(authUri)
        print("\nThen enter the auth code that is appended to redirect URI immediatly (the code is after ?code= in URI)")
        authCode = input("Auth Code: ")
        token = auth.getToken(authCode)
        if "accessToken" not in token:
            raise KeyError(token)
        print("Token: \n", token)
        accessToken = token["accessToken"]
    else:
        accessToken = input("Access Token: ")

    client = Client(EndPoints.PROTOBUF_LIVE_HOST if hostType.lower() == "live" else EndPoints.PROTOBUF_DEMO_HOST,
                    EndPoints.PROTOBUF_PORT, TcpProtocol)

    async def connected(client: Client):
        print("\n--- Connected! ---")
        request = ProtoOAApplicationAuthReq()
        request.clientId = appClientId
        request.clientSecret = appClientSecret
        try:
            await client.send(request)
        except Exception as e:
            await onError(e)

    async def disconnected(client, reason):
        print("\nDisconnected: ", reason)

    async def onMessageReceived(client, message):
        print('onMessageReceived start')

        if message.payloadType in [ProtoOASubscribeSpotsRes().payloadType, ProtoOAAccountLogoutRes().payloadType,
                                   ProtoHeartbeatEvent().payloadType]:
            return
        elif message.payloadType == ProtoOAApplicationAuthRes().payloadType:
            print("API Application authorized\n")
            print(
                "Please use setAccount command to set the authorized account before sending any other command, try help for more detail\n")
            print("To get account IDs use ProtoOAGetAccountListByAccessTokenReq command")
            if currentAccountId is not None:
                await sendProtoOAAccountAuthReq()
                return
        elif message.payloadType == ProtoOAAccountAuthRes().payloadType:
            proto_oa_account_auth_res = Protobuf.extract(message)
            print(f"Account {proto_oa_account_auth_res.ctidTraderAccountId} has been authorized\n")
            print("This account will be used for all future requests\n")
            print("You can change the account by using setAccount command")
        else:
            print("Message received: \n", Protobuf.extract(message))
        await asyncio.sleep(3)
        await executeUserCommand()

    async def onError(failure):
        raise failure
        print("Message Error: ", failure)
        await asyncio.sleep(3)
        await executeUserCommand()

    async def showHelp():
        print("Commands (Parameters with an * are required), ignore the description inside ()")
        print("setAccount(For all subsequent requests this account will be used) *accountId")
        print("ProtoOAVersionReq clientMsgId")
        print("ProtoOAGetAccountListByAccessTokenReq clientMsgId")
        print("ProtoOAAssetListReq clientMsgId")
        print("ProtoOAAssetClassListReq clientMsgId")
        print("ProtoOASymbolCategoryListReq clientMsgId")
        print("ProtoOASymbolsListReq includeArchivedSymbols(True/False) clientMsgId")
        print("ProtoOATraderReq clientMsgId")
        print("ProtoOASubscribeSpotsReq *symbolId *timeInSeconds(Unsubscribes after this time) subscribeToSpotTimestamp(True/False) clientMsgId")
        print("ProtoOAReconcileReq clientMsgId")
        print("ProtoOAGetTrendbarsReq *weeks *period *symbolId clientMsgId")
        print("ProtoOAGetTickDataReq *days *type *symbolId clientMsgId")
        print("NewMarketOrder *symbolId *tradeSide *volume clientMsgId")
        print("NewLimitOrder *symbolId *tradeSide *volume *price clientMsgId")
        print("NewStopOrder *symbolId *tradeSide *volume *price clientMsgId")
        print("ClosePosition *positionId *volume clientMsgId")
        print("CancelOrder *orderId clientMsgId")
        print("DealOffsetList *dealId clientMsgId")
        print("GetPositionUnrealizedPnL clientMsgId")
        print("OrderDetails clientMsgId")
        print("OrderListByPositionId *positionId fromTimestamp toTimestamp clientMsgId")
        await asyncio.sleep(3)
        await executeUserCommand()

    async def setAccount(account_id):
        nonlocal currentAccountId
        if currentAccountId is not None:
            await sendProtoOAAccountLogoutReq()
        currentAccountId = int(account_id)
        await sendProtoOAAccountAuthReq()

    async def sendProtoOAAccountLogoutReq(clientMsgId=None):
        request = ProtoOAAccountLogoutReq()
        request.ctidTraderAccountId = currentAccountId
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAAccountAuthReq(clientMsgId=None):
        request = ProtoOAAccountAuthReq()
        request.ctidTraderAccountId = currentAccountId
        request.accessToken = accessToken
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAVersionReq(clientMsgId=None):
        request = ProtoOAVersionReq()
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAGetAccountListByAccessTokenReq(clientMsgId=None):
        request = ProtoOAGetAccountListByAccessTokenReq()
        request.accessToken = accessToken
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAAssetListReq(clientMsgId = None):
        request = ProtoOAAssetListReq()
        request.ctidTraderAccountId = currentAccountId
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAAssetClassListReq(clientMsgId = None):
        request = ProtoOAAssetClassListReq()
        request.ctidTraderAccountId = currentAccountId
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOASymbolCategoryListReq(clientMsgId = None):
        request = ProtoOASymbolCategoryListReq()
        request.ctidTraderAccountId = currentAccountId
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOASymbolsListReq(includeArchivedSymbols = False, clientMsgId = None):
        request = ProtoOASymbolsListReq()
        request.ctidTraderAccountId = currentAccountId
        request.includeArchivedSymbols = includeArchivedSymbols if type(includeArchivedSymbols) is bool else bool(includeArchivedSymbols)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)


    async def sendProtoOATraderReq(clientMsgId = None):
        request = ProtoOATraderReq()
        request.ctidTraderAccountId = currentAccountId
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAUnsubscribeSpotsReq(symbolId, clientMsgId = None):
        request = ProtoOAUnsubscribeSpotsReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId.append(int(symbolId))
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOASubscribeSpotsReq(symbolId, timeInSeconds, subscribeToSpotTimestamp	= False, clientMsgId = None):
        request = ProtoOASubscribeSpotsReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId.append(int(symbolId))
        request.subscribeToSpotTimestamp = subscribeToSpotTimestamp if type(subscribeToSpotTimestamp) is bool else bool(subscribeToSpotTimestamp)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)
        await asyncio.sleep(int(timeInSeconds))
        await sendProtoOAUnsubscribeSpotsReq(symbolId)

    async def sendProtoOAReconcileReq(clientMsgId = None):
        request = ProtoOAReconcileReq()
        request.ctidTraderAccountId = currentAccountId
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAGetTrendbarsReq(weeks, period, symbolId, clientMsgId = None):
        request = ProtoOAGetTrendbarsReq()
        request.ctidTraderAccountId = currentAccountId
        request.period = ProtoOATrendbarPeriod.Value(period)
        request.fromTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(weeks=int(weeks))).utctimetuple())) * 1000
        request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
        request.symbolId = int(symbolId)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAGetTickDataReq(days, quoteType, symbolId, clientMsgId = None):
        request = ProtoOAGetTickDataReq()
        request.ctidTraderAccountId = currentAccountId
        request.type = ProtoOAQuoteType.Value(quoteType.upper())
        request.fromTimestamp = int(calendar.timegm((datetime.datetime.utcnow() - datetime.timedelta(days=int(days))).utctimetuple())) * 1000
        request.toTimestamp = int(calendar.timegm(datetime.datetime.utcnow().utctimetuple())) * 1000
        request.symbolId = int(symbolId)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOANewOrderReq(symbolId, orderType, tradeSide, volume, price = None, clientMsgId = None):
        request = ProtoOANewOrderReq()
        request.ctidTraderAccountId = currentAccountId
        request.symbolId = int(symbolId)
        request.orderType = ProtoOAOrderType.Value(orderType.upper())
        request.tradeSide = ProtoOATradeSide.Value(tradeSide.upper())
        request.volume = int(volume) * 100
        if request.orderType == ProtoOAOrderType.LIMIT:
            request.limitPrice = float(price)
        elif request.orderType == ProtoOAOrderType.STOP:
            request.stopPrice = float(price)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendNewMarketOrder(symbolId, tradeSide, volume, clientMsgId = None):
        sendProtoOANewOrderReq(symbolId, "MARKET", tradeSide, volume, clientMsgId = clientMsgId)

    async def sendNewLimitOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
        sendProtoOANewOrderReq(symbolId, "LIMIT", tradeSide, volume, price, clientMsgId)

    async def sendNewStopOrder(symbolId, tradeSide, volume, price, clientMsgId = None):
        sendProtoOANewOrderReq(symbolId, "STOP", tradeSide, volume, price, clientMsgId)

    async def sendProtoOAClosePositionReq(positionId, volume, clientMsgId = None):
        request = ProtoOAClosePositionReq()
        request.ctidTraderAccountId = currentAccountId
        request.positionId = int(positionId)
        request.volume = int(volume) * 100
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOACancelOrderReq(orderId, clientMsgId = None):
        request = ProtoOACancelOrderReq()
        request.ctidTraderAccountId = currentAccountId
        request.orderId = int(orderId)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOADealOffsetListReq(dealId, clientMsgId=None):
        request = ProtoOADealOffsetListReq()
        request.ctidTraderAccountId = currentAccountId
        request.dealId = int(dealId)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAGetPositionUnrealizedPnLReq(clientMsgId=None):
        request = ProtoOAGetPositionUnrealizedPnLReq()
        request.ctidTraderAccountId = currentAccountId
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAOrderDetailsReq(orderId, clientMsgId=None):
        request = ProtoOAOrderDetailsReq()
        request.ctidTraderAccountId = currentAccountId
        request.orderId = int(orderId)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    async def sendProtoOAOrderListByPositionIdReq(positionId, fromTimestamp=None, toTimestamp=None, clientMsgId=None):
        request = ProtoOAOrderListByPositionIdReq()
        request.ctidTraderAccountId = currentAccountId
        request.positionId = int(positionId)
        try:
            await client.send(request, clientMsgId=clientMsgId)
        except Exception as e:
            await onError(e)

    commands = {
        "help": showHelp,
        "setAccount": setAccount,
        "ProtoOAVersionReq": sendProtoOAVersionReq,
        "ProtoOAGetAccountListByAccessTokenReq": sendProtoOAGetAccountListByAccessTokenReq,
        "ProtoOAAssetListReq": sendProtoOAAssetListReq,
        "ProtoOAAssetClassListReq": sendProtoOAAssetClassListReq,
        "ProtoOASymbolCategoryListReq": sendProtoOASymbolCategoryListReq,
        "ProtoOASymbolsListReq": sendProtoOASymbolsListReq,
        "ProtoOATraderReq": sendProtoOATraderReq,
        "ProtoOASubscribeSpotsReq": sendProtoOASubscribeSpotsReq,
        "ProtoOAReconcileReq": sendProtoOAReconcileReq,
        "ProtoOAGetTrendbarsReq": sendProtoOAGetTrendbarsReq,
        "ProtoOAGetTickDataReq": sendProtoOAGetTickDataReq,
        "NewMarketOrder": sendNewMarketOrder,
        "NewLimitOrder": sendNewLimitOrder,
        "NewStopOrder": sendNewStopOrder,
        "ClosePosition": sendProtoOAClosePositionReq,
        "CancelOrder": sendProtoOACancelOrderReq,
        "DealOffsetList": sendProtoOADealOffsetListReq,
        "GetPositionUnrealizedPnL": sendProtoOAGetPositionUnrealizedPnLReq,
        "OrderDetails": sendProtoOAOrderDetailsReq,
        "OrderListByPositionId": sendProtoOAOrderListByPositionIdReq,
    }

    async def executeUserCommand():
        try:
            print("\n")
            user_input = await asyncio.wait_for(asyncio.to_thread(inputimeout, "Command (ex help): ", 18), 18)
        except TimeoutOccurred:
            print("Command Input Timeout: TimeoutOccurred")
            await asyncio.sleep(3)
            await executeUserCommand()
            return
        except asyncio.TimeoutError:
            print("Command Input Timeout: asyncio.TimeoutError")
            await asyncio.sleep(3)
            await executeUserCommand()
            return

        user_input_split = user_input.split(" ")
        if not user_input_split:
            print("Command split error: ", user_input)
            await asyncio.sleep(3)
            await executeUserCommand()
            return

        command = user_input_split[0]
        try:
            parameters = [parameter if parameter[0] != "*" else parameter[1:] for parameter in user_input_split[1:]]
        except Exception:
            print("Invalid parameters: ", user_input)
            await asyncio.sleep(3)
            await executeUserCommand()
            return

        if command in commands:
            await commands[command](*parameters)
        else:
            print("Invalid Command: ", user_input)
            await asyncio.sleep(3)
            await executeUserCommand()

    client.setConnectedCallback(connected)
    client.setDisconnectedCallback(disconnected)
    client.setMessageReceivedCallback(onMessageReceived)

    await client.start()
    await asyncio.sleep(3)
    await executeUserCommand()

if __name__ == "__main__":
    asyncio.run(main())
