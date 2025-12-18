"""
CTrader OpenAPI Protobuf Classes Reference

This file contains Python class representations of the protobuf messages
found in the ctrader_open_api.messages package. These classes show the
structure and attributes of each protobuf message type for easy reference.

Note: These are reference classes only. The actual protobuf classes are
automatically generated and should be imported from the messages package.
"""

from typing import Optional, List
from enum import Enum

# =============================================================================
# COMMON MESSAGE CLASSES (OpenApiCommonMessages_pb2.py)
# =============================================================================

class ProtoMessage:
    """Main container for all messages"""
    payloadType: int  # required - type of payload
    payload: bytes    # optional - serialized payload data
    clientMsgId: str  # optional - client message ID

class ProtoErrorRes:
    """Error response message"""
    payloadType: int  # ERROR_RES payload type
    errorCode: str    # required - error code
    description: str  # optional - error description
    maintenanceEndTimestamp: int  # optional - maintenance end time

class ProtoHeartbeatEvent:
    """Heartbeat event message"""
    payloadType: int  # HEARTBEAT_EVENT payload type

# =============================================================================
# COMMON MODEL ENUMS (OpenApiCommonModelMessages_pb2.py)
# =============================================================================

class ProtoPayloadType(Enum):
    """Payload type identifiers"""
    PROTO_MESSAGE = 5
    ERROR_RES = 50
    HEARTBEAT_EVENT = 51

class ProtoErrorCode(Enum):
    """Common error codes"""
    UNKNOWN_ERROR = 1
    UNSUPPORTED_MESSAGE = 2
    INVALID_REQUEST = 3
    TIMEOUT_ERROR = 5
    ENTITY_NOT_FOUND = 6
    CANT_ROUTE_REQUEST = 7
    FRAME_TOO_LONG = 8
    MARKET_CLOSED = 9
    CONCURRENT_MODIFICATION = 10
    BLOCKED_PAYLOAD_TYPE = 11

# =============================================================================
# MAIN API MESSAGE CLASSES (OpenApiMessages_pb2.py)
# =============================================================================

class ProtoOAApplicationAuthReq:
    """Application authentication request"""
    payloadType: int  # PROTO_OA_APPLICATION_AUTH_REQ
    clientId: str     # required - application client ID
    clientSecret: str # required - application client secret

class ProtoOAApplicationAuthRes:
    """Application authentication response"""
    payloadType: int  # PROTO_OA_APPLICATION_AUTH_RES

class ProtoOAAccountAuthReq:
    """Account authentication request"""
    payloadType: int          # PROTO_OA_ACCOUNT_AUTH_REQ
    ctidTraderAccountId: int  # required - trader account ID
    accessToken: str          # required - OAuth access token

class ProtoOAAccountAuthRes:
    """Account authentication response"""
    payloadType: int          # PROTO_OA_ACCOUNT_AUTH_RES
    ctidTraderAccountId: int  # required - trader account ID

class ProtoOAErrorRes:
    """OpenAPI error response"""
    payloadType: int                # PROTO_OA_ERROR_RES
    ctidTraderAccountId: int        # optional - trader account ID
    errorCode: str                  # required - error code
    description: str                # optional - error description
    maintenanceEndTimestamp: int    # optional - maintenance end time

class ProtoOAVersionReq:
    """Version request"""
    payloadType: int  # PROTO_OA_VERSION_REQ

class ProtoOAVersionRes:
    """Version response"""
    payloadType: int  # PROTO_OA_VERSION_RES
    version: str      # required - API version

class ProtoOANewOrderReq:
    """New order request"""
    payloadType: int              # PROTO_OA_NEW_ORDER_REQ
    ctidTraderAccountId: int      # required
    symbolId: int                 # required - symbol identifier
    orderType: int                # required - ProtoOAOrderType enum
    tradeSide: int                # required - ProtoOATradeSide enum (BUY/SELL)
    volume: int                   # required - volume in cents
    limitPrice: float             # optional - limit price
    stopPrice: float              # optional - stop price
    timeInForce: int              # optional - ProtoOATimeInForce enum
    expirationTimestamp: int      # optional - expiration time
    stopLoss: float               # optional - stop loss price
    takeProfit: float             # optional - take profit price
    comment: str                  # optional - order comment
    baseSlippagePrice: float      # optional - base slippage price
    slippageInPoints: int         # optional - slippage in points
    label: str                    # optional - order label
    positionId: int               # optional - position ID for closing
    clientOrderId: str            # optional - client order ID
    relativeStopLoss: int         # optional - relative SL in points
    relativeTakeProfit: int       # optional - relative TP in points
    guaranteedStopLoss: bool      # optional - guaranteed stop loss
    trailingStopLoss: bool        # optional - trailing stop loss
    stopTriggerMethod: int        # optional - ProtoOAOrderTriggerMethod

class ProtoOAExecutionEvent:
    """Order execution event"""
    payloadType: int                    # PROTO_OA_EXECUTION_EVENT
    ctidTraderAccountId: int            # required
    executionType: int                  # required - ProtoOAExecutionType
    position: 'ProtoOAPosition'         # optional - position data
    order: 'ProtoOAOrder'               # optional - order data
    deal: 'ProtoOADeal'                 # optional - deal data
    bonusDepositWithdraw: 'ProtoOABonusDepositWithdraw'  # optional
    depositWithdraw: 'ProtoOADepositWithdraw'            # optional
    errorCode: str                      # optional - error code
    isServerEvent: bool                 # optional - server event flag

class ProtoOACancelOrderReq:
    """Cancel order request"""
    payloadType: int          # PROTO_OA_CANCEL_ORDER_REQ
    ctidTraderAccountId: int  # required
    orderId: int              # required - order ID to cancel

class ProtoOAAmendOrderReq:
    """Amend order request"""
    payloadType: int              # PROTO_OA_AMEND_ORDER_REQ
    ctidTraderAccountId: int      # required
    orderId: int                  # required - order ID to amend
    volume: int                   # optional - new volume
    limitPrice: float             # optional - new limit price
    stopPrice: float              # optional - new stop price
    expirationTimestamp: int      # optional - new expiration
    stopLoss: float               # optional - new stop loss
    takeProfit: float             # optional - new take profit
    slippageInPoints: int         # optional - new slippage
    relativeStopLoss: int         # optional - new relative SL
    relativeTakeProfit: int       # optional - new relative TP
    guaranteedStopLoss: bool      # optional - GSL flag
    trailingStopLoss: bool        # optional - trailing SL flag
    stopTriggerMethod: int        # optional - trigger method

class ProtoOAAmendPositionSLTPReq:
    """Amend position stop loss/take profit request"""
    payloadType: int              # PROTO_OA_AMEND_POSITION_SLTP_REQ
    ctidTraderAccountId: int      # required
    positionId: int               # required
    stopLoss: float               # optional - new stop loss
    takeProfit: float             # optional - new take profit
    guaranteedStopLoss: bool      # optional - GSL flag
    trailingStopLoss: bool        # optional - trailing SL flag
    stopLossTriggerMethod: int    # optional - SL trigger method

class ProtoOAClosePositionReq:
    """Close position request"""
    payloadType: int          # PROTO_OA_CLOSE_POSITION_REQ
    ctidTraderAccountId: int  # required
    positionId: int           # required
    volume: int               # required - volume to close

class ProtoOAAssetListReq:
    """Asset list request"""
    payloadType: int          # PROTO_OA_ASSET_LIST_REQ
    ctidTraderAccountId: int  # required

class ProtoOAAssetListRes:
    """Asset list response"""
    payloadType: int               # PROTO_OA_ASSET_LIST_RES
    ctidTraderAccountId: int       # required
    asset: List['ProtoOAAsset']    # repeated - list of assets

class ProtoOASymbolsListReq:
    """Symbols list request"""
    payloadType: int               # PROTO_OA_SYMBOLS_LIST_REQ
    ctidTraderAccountId: int       # required
    includeArchivedSymbols: bool   # optional - include archived symbols

class ProtoOASymbolsListRes:
    """Symbols list response"""
    payloadType: int                         # PROTO_OA_SYMBOLS_LIST_RES
    ctidTraderAccountId: int                 # required
    symbol: List['ProtoOALightSymbol']       # repeated - active symbols
    archivedSymbol: List['ProtoOAArchivedSymbol']  # repeated - archived symbols

class ProtoOATraderReq:
    """Trader request"""
    payloadType: int          # PROTO_OA_TRADER_REQ
    ctidTraderAccountId: int  # required

class ProtoOATraderRes:
    """Trader response"""
    payloadType: int          # PROTO_OA_TRADER_RES
    ctidTraderAccountId: int  # required
    trader: 'ProtoOATrader'   # required - trader information

class ProtoOAReconcileReq:
    """Reconcile request"""
    payloadType: int          # PROTO_OA_RECONCILE_REQ
    ctidTraderAccountId: int  # required

class ProtoOAReconcileRes:
    """Reconcile response"""
    payloadType: int                  # PROTO_OA_RECONCILE_RES
    ctidTraderAccountId: int          # required
    position: List['ProtoOAPosition'] # repeated - positions
    order: List['ProtoOAOrder']       # repeated - orders

class ProtoOASubscribeSpotsReq:
    """Subscribe to spot prices request"""
    payloadType: int               # PROTO_OA_SUBSCRIBE_SPOTS_REQ
    ctidTraderAccountId: int       # required
    symbolId: List[int]            # repeated - symbol IDs
    subscribeToSpotTimestamp: bool # optional - subscribe to timestamps

class ProtoOASpotEvent:
    """Spot price event"""
    payloadType: int                    # PROTO_OA_SPOT_EVENT
    ctidTraderAccountId: int            # required
    symbolId: int                       # required
    bid: int                           # optional - bid price (in cents)
    ask: int                           # optional - ask price (in cents)
    trendbar: List['ProtoOATrendbar']  # repeated - trendbar data
    sessionClose: int                  # optional - session close price
    timestamp: int                     # optional - timestamp

class ProtoOAGetTrendbarsReq:
    """Get trendbars request"""
    payloadType: int          # PROTO_OA_GET_TRENDBARS_REQ
    ctidTraderAccountId: int  # required
    fromTimestamp: int        # required - start time
    toTimestamp: int          # required - end time
    period: int               # required - ProtoOATrendbarPeriod
    symbolId: int             # required
    count: int                # optional - number of bars

class ProtoOAGetTrendbarsRes:
    """Get trendbars response"""
    payloadType: int                    # PROTO_OA_GET_TRENDBARS_RES
    ctidTraderAccountId: int            # required
    period: int                         # required - ProtoOATrendbarPeriod
    timestamp: List[int]                # repeated - timestamps
    trendbar: List['ProtoOATrendbar']   # repeated - trendbar data
    symbolId: int                       # optional - symbol ID

# =============================================================================
# MODEL MESSAGE CLASSES (OpenApiModelMessages_pb2.py)
# =============================================================================

class ProtoOAAsset:
    """Asset information"""
    assetId: int        # required - asset ID
    name: str           # required - asset name
    displayName: str    # optional - display name
    digits: int         # optional - decimal digits

class ProtoOASymbol:
    """Symbol information"""
    symbolId: int                    # required
    digits: int                      # required - price digits
    pipPosition: int                 # required - pip position
    enableShortSelling: bool         # optional - short selling allowed
    guaranteedStopLoss: bool         # optional - GSL allowed
    swapRollover3Days: int          # optional - ProtoOADayOfWeek
    swapLong: float                 # optional - long swap
    swapShort: float                # optional - short swap
    maxVolume: int                  # optional - max volume
    minVolume: int                  # optional - min volume
    stepVolume: int                 # optional - step volume
    maxExposure: int                # optional - max exposure
    schedule: List['ProtoOAInterval'] # repeated - trading schedule
    commission: int                 # optional - deprecated
    commissionType: int             # optional - ProtoOACommissionType
    slDistance: int                 # optional - SL distance
    tpDistance: int                 # optional - TP distance
    gslDistance: int                # optional - GSL distance
    gslCharge: int                  # optional - GSL charge
    distanceSetIn: int              # optional - ProtoOASymbolDistanceType
    minCommission: int              # optional - deprecated
    minCommissionType: int          # optional - ProtoOAMinCommissionType
    minCommissionAsset: str         # optional - min commission asset
    rolloverCommission: int         # optional - rollover commission
    skipRolloverDays: int           # optional - skip rollover days
    scheduleTimeZone: str           # optional - timezone
    tradingMode: int                # optional - ProtoOATradingMode
    rolloverCommission3Days: int    # optional - 3-day rollover
    swapCalculationType: int        # optional - ProtoOASwapCalculationType
    lotSize: int                    # optional - lot size
    preciseTradingCommissionRate: int # optional - precise commission
    preciseMinCommission: int       # optional - precise min commission
    holiday: List['ProtoOAHoliday'] # repeated - holidays
    pnlConversionFeeRate: int       # optional - PnL conversion fee
    leverageId: int                 # optional - leverage ID
    swapPeriod: int                 # optional - swap period
    swapTime: int                   # optional - swap time
    skipSWAPPeriods: int            # optional - skip swap periods
    chargeSwapAtWeekends: bool      # optional - weekend swap charge

class ProtoOALightSymbol:
    """Light symbol information"""
    symbolId: int           # required
    symbolName: str         # optional - symbol name
    enabled: bool           # optional - is enabled
    baseAssetId: int        # optional - base asset ID
    quoteAssetId: int       # optional - quote asset ID
    symbolCategoryId: int   # optional - category ID
    description: str        # optional - description

class ProtoOATrader:
    """Trader account information"""
    ctidTraderAccountId: int                    # required
    balance: int                                # required - balance in cents
    balanceVersion: int                         # optional - balance version
    managerBonus: int                          # optional - manager bonus
    ibBonus: int                               # optional - IB bonus
    nonWithdrawableBonus: int                  # optional - non-withdrawable bonus
    accessRights: int                          # optional - ProtoOAAccessRights
    depositAssetId: int                        # required - deposit asset ID
    swapFree: bool                             # optional - swap free account
    leverageInCents: int                       # optional - leverage in cents
    totalMarginCalculationType: int            # optional - margin calculation type
    maxLeverage: int                           # optional - max leverage
    frenchRisk: bool                           # optional - deprecated
    traderLogin: int                           # optional - trader login
    accountType: int                           # optional - ProtoOAAccountType
    brokerName: str                            # optional - broker name
    registrationTimestamp: int                 # optional - registration time
    isLimitedRisk: bool                        # optional - limited risk flag
    limitedRiskMarginCalculationStrategy: int  # optional - risk calculation strategy
    moneyDigits: int                           # optional - money digits

class ProtoOAPosition:
    """Position information"""
    positionId: int                   # required
    tradeData: 'ProtoOATradeData'     # required - trade data
    positionStatus: int               # required - ProtoOAPositionStatus
    swap: int                         # required - swap in cents
    price: float                      # optional - current price
    stopLoss: float                   # optional - stop loss price
    takeProfit: float                 # optional - take profit price
    utcLastUpdateTimestamp: int       # optional - last update time
    commission: int                   # optional - commission
    marginRate: float                 # optional - margin rate
    mirroringCommission: int          # optional - mirroring commission
    guaranteedStopLoss: bool          # optional - GSL flag
    usedMargin: int                   # optional - used margin
    stopLossTriggerMethod: int        # optional - SL trigger method
    moneyDigits: int                  # optional - money digits
    trailingStopLoss: bool            # optional - trailing SL flag

class ProtoOATradeData:
    """Trade data"""
    symbolId: int           # required
    volume: int             # required - volume in cents
    tradeSide: int          # required - ProtoOATradeSide
    openTimestamp: int      # optional - open time
    label: str              # optional - label
    guaranteedStopLoss: bool # optional - GSL flag
    comment: str            # optional - comment

class ProtoOAOrder:
    """Order information"""
    orderId: int                    # required
    tradeData: 'ProtoOATradeData'   # required - trade data
    orderType: int                  # required - ProtoOAOrderType
    orderStatus: int                # required - ProtoOAOrderStatus
    expirationTimestamp: int        # optional - expiration time
    executionPrice: float           # optional - execution price
    executedVolume: int             # optional - executed volume
    utcLastUpdateTimestamp: int     # optional - last update time
    baseSlippagePrice: float        # optional - base slippage price
    slippageInPoints: int           # optional - slippage in points
    closingOrder: bool              # optional - closing order flag
    limitPrice: float               # optional - limit price
    stopPrice: float                # optional - stop price
    stopLoss: float                 # optional - stop loss
    takeProfit: float               # optional - take profit
    clientOrderId: str              # optional - client order ID
    timeInForce: int                # optional - ProtoOATimeInForce
    positionId: int                 # optional - position ID
    relativeStopLoss: int           # optional - relative SL
    relativeTakeProfit: int         # optional - relative TP
    isStopOut: bool                 # optional - stop out flag
    trailingStopLoss: bool          # optional - trailing SL flag
    stopTriggerMethod: int          # optional - trigger method

class ProtoOADeal:
    """Deal information"""
    dealId: int                              # required
    orderId: int                             # required
    positionId: int                          # required
    volume: int                              # required - volume in cents
    filledVolume: int                        # required - filled volume
    symbolId: int                            # required
    createTimestamp: int                     # required - creation time
    executionTimestamp: int                  # required - execution time
    utcLastUpdateTimestamp: int              # optional - last update time
    executionPrice: float                    # optional - execution price
    tradeSide: int                           # required - ProtoOATradeSide
    dealStatus: int                          # required - ProtoOADealStatus
    marginRate: float                        # optional - margin rate
    commission: int                          # optional - commission
    baseToUsdConversionRate: float           # optional - conversion rate
    closePositionDetail: 'ProtoOAClosePositionDetail' # optional
    moneyDigits: int                         # optional - money digits

class ProtoOAClosePositionDetail:
    """Close position details"""
    entryPrice: float                    # required - entry price
    grossProfit: int                     # required - gross profit
    swap: int                            # required - swap
    commission: int                      # required - commission
    balance: int                         # required - balance
    quoteToDepositConversionRate: float  # optional - conversion rate
    closedVolume: int                    # optional - closed volume
    balanceVersion: int                  # optional - balance version
    moneyDigits: int                     # optional - money digits
    pnlConversionFee: int                # optional - PnL conversion fee

class ProtoOATrendbar:
    """Trendbar data"""
    volume: int                       # required - volume
    period: int                       # optional - ProtoOATrendbarPeriod
    low: int                          # optional - low price (in cents)
    deltaOpen: int                    # optional - open delta
    deltaClose: int                   # optional - close delta
    deltaHigh: int                    # optional - high delta
    utcTimestampInMinutes: int        # optional - timestamp in minutes

class ProtoOATickData:
    """Tick data"""
    timestamp: int  # required - timestamp
    tick: int       # required - tick value

# =============================================================================
# ENUMS FROM MODEL MESSAGES
# =============================================================================

class ProtoOAPayloadType(Enum):
    """OpenAPI payload types (partial list)"""
    PROTO_OA_APPLICATION_AUTH_REQ = 2100
    PROTO_OA_APPLICATION_AUTH_RES = 2101
    PROTO_OA_ACCOUNT_AUTH_REQ = 2102
    PROTO_OA_ACCOUNT_AUTH_RES = 2103
    PROTO_OA_VERSION_REQ = 2104
    PROTO_OA_VERSION_RES = 2105
    PROTO_OA_NEW_ORDER_REQ = 2106
    PROTO_OA_EXECUTION_EVENT = 2122
    # ... many more values

class ProtoOATradeSide(Enum):
    """Trade side"""
    BUY = 1
    SELL = 2

class ProtoOAOrderType(Enum):
    """Order types"""
    MARKET = 1
    LIMIT = 2
    STOP = 3
    STOP_LOSS_TAKE_PROFIT = 4
    MARKET_RANGE = 5
    STOP_LIMIT = 6

class ProtoOATimeInForce(Enum):
    """Time in force options"""
    GOOD_TILL_DATE = 1
    GOOD_TILL_CANCEL = 2
    IMMEDIATE_OR_CANCEL = 3
    FILL_OR_KILL = 4
    MARKET_ON_OPEN = 5

class ProtoOAOrderStatus(Enum):
    """Order status"""
    ORDER_STATUS_ACCEPTED = 1
    ORDER_STATUS_FILLED = 2
    ORDER_STATUS_REJECTED = 3
    ORDER_STATUS_EXPIRED = 4
    ORDER_STATUS_CANCELLED = 5

class ProtoOAPositionStatus(Enum):
    """Position status"""
    POSITION_STATUS_OPEN = 1
    POSITION_STATUS_CLOSED = 2
    POSITION_STATUS_CREATED = 3
    POSITION_STATUS_ERROR = 4

class ProtoOAExecutionType(Enum):
    """Execution types"""
    ORDER_ACCEPTED = 2
    ORDER_FILLED = 3
    ORDER_REPLACED = 4
    ORDER_CANCELLED = 5
    ORDER_EXPIRED = 6
    ORDER_REJECTED = 7
    ORDER_CANCEL_REJECTED = 8
    SWAP = 9
    DEPOSIT_WITHDRAW = 10
    ORDER_PARTIAL_FILL = 11
    BONUS_DEPOSIT_WITHDRAW = 12

class ProtoOATrendbarPeriod(Enum):
    """Trendbar periods"""
    M1 = 1   # 1 minute
    M2 = 2   # 2 minutes
    M3 = 3   # 3 minutes
    M4 = 4   # 4 minutes
    M5 = 5   # 5 minutes
    M10 = 6  # 10 minutes
    M15 = 7  # 15 minutes
    M30 = 8  # 30 minutes
    H1 = 9   # 1 hour
    H4 = 10  # 4 hours
    H12 = 11 # 12 hours
    D1 = 12  # 1 day
    W1 = 13  # 1 week
    MN1 = 14 # 1 month

class ProtoOAAccessRights(Enum):
    """Account access rights"""
    FULL_ACCESS = 0
    CLOSE_ONLY = 1
    NO_TRADING = 2
    NO_LOGIN = 3

class ProtoOAAccountType(Enum):
    """Account types"""
    HEDGED = 0
    NETTED = 1
    SPREAD_BETTING = 2

class ProtoOADayOfWeek(Enum):
    """Days of the week"""
    NONE = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

class ProtoOATradingMode(Enum):
    """Trading modes"""
    ENABLED = 0
    DISABLED_WITHOUT_PENDINGS_EXECUTION = 1
    DISABLED_WITH_PENDINGS_EXECUTION = 2
    CLOSE_ONLY_MODE = 3

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def example_usage():
    """
    Example of how to use the actual protobuf classes
    (this is just for reference - use the generated classes)
    """
    # Import the actual generated classes
    from ctrader_open_api.messages.OpenApiMessages_pb2 import (
        ProtoOAApplicationAuthReq,
        ProtoOANewOrderReq,
        ProtoOASubscribeSpotsReq
    )
    from ctrader_open_api.messages.OpenApiModelMessages_pb2 import (
        ProtoOAPayloadType,
        ProtoOATradeSide,
        ProtoOAOrderType
    )

    # Example: Create authentication request
    auth_req = ProtoOAApplicationAuthReq()
    auth_req.payloadType = ProtoOAPayloadType.PROTO_OA_APPLICATION_AUTH_REQ
    auth_req.clientId = "your_client_id"
    auth_req.clientSecret = "your_client_secret"

    # Example: Create new order request
    order_req = ProtoOANewOrderReq()
    order_req.payloadType = ProtoOAPayloadType.PROTO_OA_NEW_ORDER_REQ
    order_req.ctidTraderAccountId = 12345
    order_req.symbolId = 1  # EURUSD
    order_req.orderType = ProtoOAOrderType.MARKET
    order_req.tradeSide = ProtoOATradeSide.BUY
    order_req.volume = 100000  # 0.01 lot in cents

    # Example: Subscribe to spots
    spots_req = ProtoOASubscribeSpotsReq()
    spots_req.payloadType = ProtoOAPayloadType.PROTO_OA_SUBSCRIBE_SPOTS_REQ
    spots_req.ctidTraderAccountId = 12345
    spots_req.symbolId.extend([1, 2, 3])  # Multiple symbol IDs

if __name__ == "__main__":
    print("CTrader OpenAPI Protobuf Classes Reference")
    print("==========================================")
    print()
    print("This file contains class definitions showing the structure")
    print("of all protobuf messages in the CTrader OpenAPI.")
    print()
    print("To use the actual protobuf classes, import them from:")
    print("- ctrader_open_api.messages.OpenApiMessages_pb2")
    print("- ctrader_open_api.messages.OpenApiModelMessages_pb2")
    print("- ctrader_open_api.messages.OpenApiCommonMessages_pb2")
    print("- ctrader_open_api.messages.OpenApiCommonModelMessages_pb2")