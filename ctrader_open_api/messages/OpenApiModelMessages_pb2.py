# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: OpenApiModelMessages.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor, descriptor_pool as _descriptor_pool, \
    symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1aOpenApiModelMessages.proto\"R\n\x0cProtoOAAsset\x12\x0f\n\x07\x61ssetId\x18\x01 \x02(\x03\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x13\n\x0b\x64isplayName\x18\x03 \x01(\t\x12\x0e\n\x06\x64igits\x18\x04 \x01(\x05\"\xc8\t\n\rProtoOASymbol\x12\x10\n\x08symbolId\x18\x01 \x02(\x03\x12\x0e\n\x06\x64igits\x18\x02 \x02(\x05\x12\x13\n\x0bpipPosition\x18\x03 \x02(\x05\x12\x1a\n\x12\x65nableShortSelling\x18\x04 \x01(\x08\x12\x1a\n\x12guaranteedStopLoss\x18\x05 \x01(\x08\x12\x34\n\x11swapRollover3Days\x18\x06 \x01(\x0e\x32\x11.ProtoOADayOfWeek:\x06MONDAY\x12\x10\n\x08swapLong\x18\x07 \x01(\x01\x12\x11\n\tswapShort\x18\x08 \x01(\x01\x12\x11\n\tmaxVolume\x18\t \x01(\x03\x12\x11\n\tminVolume\x18\n \x01(\x03\x12\x12\n\nstepVolume\x18\x0b \x01(\x03\x12\x13\n\x0bmaxExposure\x18\x0c \x01(\x04\x12\"\n\x08schedule\x18\r \x03(\x0b\x32\x10.ProtoOAInterval\x12\x16\n\ncommission\x18\x0e \x01(\x03\x42\x02\x18\x01\x12\x43\n\x0e\x63ommissionType\x18\x0f \x01(\x0e\x32\x16.ProtoOACommissionType:\x13USD_PER_MILLION_USD\x12\x12\n\nslDistance\x18\x10 \x01(\r\x12\x12\n\ntpDistance\x18\x11 \x01(\r\x12\x13\n\x0bgslDistance\x18\x12 \x01(\r\x12\x11\n\tgslCharge\x18\x13 \x01(\x03\x12L\n\rdistanceSetIn\x18\x14 \x01(\x0e\x32\x1a.ProtoOASymbolDistanceType:\x19SYMBOL_DISTANCE_IN_POINTS\x12\x19\n\rminCommission\x18\x15 \x01(\x03\x42\x02\x18\x01\x12>\n\x11minCommissionType\x18\x16 \x01(\x0e\x32\x19.ProtoOAMinCommissionType:\x08\x43URRENCY\x12\x1f\n\x12minCommissionAsset\x18\x17 \x01(\t:\x03USD\x12\x1a\n\x12rolloverCommission\x18\x18 \x01(\x03\x12\x18\n\x10skipRolloverDays\x18\x19 \x01(\x05\x12\x18\n\x10scheduleTimeZone\x18\x1a \x01(\t\x12\x31\n\x0btradingMode\x18\x1b \x01(\x0e\x32\x13.ProtoOATradingMode:\x07\x45NABLED\x12:\n\x17rolloverCommission3Days\x18\x1c \x01(\x0e\x32\x11.ProtoOADayOfWeek:\x06MONDAY\x12>\n\x13swapCalculationType\x18\x1d \x01(\x0e\x32\x1b.ProtoOASwapCalculationType:\x04PIPS\x12\x0f\n\x07lotSize\x18\x1e \x01(\x03\x12$\n\x1cpreciseTradingCommissionRate\x18\x1f \x01(\x03\x12\x1c\n\x14preciseMinCommission\x18  \x01(\x03\x12 \n\x07holiday\x18! \x03(\x0b\x32\x0f.ProtoOAHoliday\x12\x1c\n\x14pnlConversionFeeRate\x18\" \x01(\x05\x12\x12\n\nleverageId\x18# \x01(\x03\x12\x12\n\nswapPeriod\x18$ \x01(\x05\x12\x10\n\x08swapTime\x18% \x01(\x05\x12\x17\n\x0fskipSWAPPeriods\x18& \x01(\x05\x12\x1c\n\x14\x63hargeSwapAtWeekends\x18\' \x01(\x08\"\xa5\x01\n\x12ProtoOALightSymbol\x12\x10\n\x08symbolId\x18\x01 \x02(\x03\x12\x12\n\nsymbolName\x18\x02 \x01(\t\x12\x0f\n\x07\x65nabled\x18\x03 \x01(\x08\x12\x13\n\x0b\x62\x61seAssetId\x18\x04 \x01(\x03\x12\x14\n\x0cquoteAssetId\x18\x05 \x01(\x03\x12\x18\n\x10symbolCategoryId\x18\x06 \x01(\x03\x12\x13\n\x0b\x64\x65scription\x18\x07 \x01(\t\"l\n\x15ProtoOAArchivedSymbol\x12\x10\n\x08symbolId\x18\x01 \x02(\x03\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x1e\n\x16utcLastUpdateTimestamp\x18\x03 \x02(\x03\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\t\"G\n\x15ProtoOASymbolCategory\x12\n\n\x02id\x18\x01 \x02(\x03\x12\x14\n\x0c\x61ssetClassId\x18\x02 \x02(\x03\x12\x0c\n\x04name\x18\x03 \x02(\t\"9\n\x0fProtoOAInterval\x12\x13\n\x0bstartSecond\x18\x03 \x02(\r\x12\x11\n\tendSecond\x18\x04 \x02(\r\"\xa4\x05\n\rProtoOATrader\x12\x1b\n\x13\x63tidTraderAccountId\x18\x01 \x02(\x03\x12\x0f\n\x07\x62\x61lance\x18\x02 \x02(\x03\x12\x16\n\x0e\x62\x61lanceVersion\x18\x03 \x01(\x03\x12\x14\n\x0cmanagerBonus\x18\x04 \x01(\x03\x12\x0f\n\x07ibBonus\x18\x05 \x01(\x03\x12\x1c\n\x14nonWithdrawableBonus\x18\x06 \x01(\x03\x12\x37\n\x0c\x61\x63\x63\x65ssRights\x18\x07 \x01(\x0e\x32\x14.ProtoOAAccessRights:\x0b\x46ULL_ACCESS\x12\x16\n\x0e\x64\x65positAssetId\x18\x08 \x02(\x03\x12\x10\n\x08swapFree\x18\t \x01(\x08\x12\x17\n\x0fleverageInCents\x18\n \x01(\r\x12\x46\n\x1atotalMarginCalculationType\x18\x0b \x01(\x0e\x32\".ProtoOATotalMarginCalculationType\x12\x13\n\x0bmaxLeverage\x18\x0c \x01(\r\x12\x16\n\nfrenchRisk\x18\r \x01(\x08\x42\x02\x18\x01\x12\x13\n\x0btraderLogin\x18\x0e \x01(\x03\x12\x30\n\x0b\x61\x63\x63ountType\x18\x0f \x01(\x0e\x32\x13.ProtoOAAccountType:\x06HEDGED\x12\x12\n\nbrokerName\x18\x10 \x01(\t\x12\x1d\n\x15registrationTimestamp\x18\x11 \x01(\x03\x12\x15\n\risLimitedRisk\x18\x12 \x01(\x08\x12q\n$limitedRiskMarginCalculationStrategy\x18\x13 \x01(\x0e\x32,.ProtoOALimitedRiskMarginCalculationStrategy:\x15\x41\x43\x43ORDING_TO_LEVERAGE\x12\x13\n\x0bmoneyDigits\x18\x14 \x01(\r\"\xc4\x03\n\x0fProtoOAPosition\x12\x12\n\npositionId\x18\x01 \x02(\x03\x12$\n\ttradeData\x18\x02 \x02(\x0b\x32\x11.ProtoOATradeData\x12.\n\x0epositionStatus\x18\x03 \x02(\x0e\x32\x16.ProtoOAPositionStatus\x12\x0c\n\x04swap\x18\x04 \x02(\x03\x12\r\n\x05price\x18\x05 \x01(\x01\x12\x10\n\x08stopLoss\x18\x06 \x01(\x01\x12\x12\n\ntakeProfit\x18\x07 \x01(\x01\x12\x1e\n\x16utcLastUpdateTimestamp\x18\x08 \x01(\x03\x12\x12\n\ncommission\x18\t \x01(\x03\x12\x12\n\nmarginRate\x18\n \x01(\x01\x12\x1b\n\x13mirroringCommission\x18\x0b \x01(\x03\x12\x1a\n\x12guaranteedStopLoss\x18\x0c \x01(\x08\x12\x12\n\nusedMargin\x18\r \x01(\x04\x12@\n\x15stopLossTriggerMethod\x18\x0e \x01(\x0e\x32\x1a.ProtoOAOrderTriggerMethod:\x05TRADE\x12\x13\n\x0bmoneyDigits\x18\x0f \x01(\r\x12\x18\n\x10trailingStopLoss\x18\x10 \x01(\x08\"\xad\x01\n\x10ProtoOATradeData\x12\x10\n\x08symbolId\x18\x01 \x02(\x03\x12\x0e\n\x06volume\x18\x02 \x02(\x03\x12$\n\ttradeSide\x18\x03 \x02(\x0e\x32\x11.ProtoOATradeSide\x12\x15\n\ropenTimestamp\x18\x04 \x01(\x03\x12\r\n\x05label\x18\x05 \x01(\t\x12\x1a\n\x12guaranteedStopLoss\x18\x06 \x01(\x08\x12\x0f\n\x07\x63omment\x18\x07 \x01(\t\"\xa5\x05\n\x0cProtoOAOrder\x12\x0f\n\x07orderId\x18\x01 \x02(\x03\x12$\n\ttradeData\x18\x02 \x02(\x0b\x32\x11.ProtoOATradeData\x12$\n\torderType\x18\x03 \x02(\x0e\x32\x11.ProtoOAOrderType\x12(\n\x0borderStatus\x18\x04 \x02(\x0e\x32\x13.ProtoOAOrderStatus\x12\x1b\n\x13\x65xpirationTimestamp\x18\x06 \x01(\x03\x12\x16\n\x0e\x65xecutionPrice\x18\x07 \x01(\x01\x12\x16\n\x0e\x65xecutedVolume\x18\x08 \x01(\x03\x12\x1e\n\x16utcLastUpdateTimestamp\x18\t \x01(\x03\x12\x19\n\x11\x62\x61seSlippagePrice\x18\n \x01(\x01\x12\x18\n\x10slippageInPoints\x18\x0b \x01(\x03\x12\x14\n\x0c\x63losingOrder\x18\x0c \x01(\x08\x12\x12\n\nlimitPrice\x18\r \x01(\x01\x12\x11\n\tstopPrice\x18\x0e \x01(\x01\x12\x10\n\x08stopLoss\x18\x0f \x01(\x01\x12\x12\n\ntakeProfit\x18\x10 \x01(\x01\x12\x15\n\rclientOrderId\x18\x11 \x01(\t\x12=\n\x0btimeInForce\x18\x12 \x01(\x0e\x32\x13.ProtoOATimeInForce:\x13IMMEDIATE_OR_CANCEL\x12\x12\n\npositionId\x18\x13 \x01(\x03\x12\x18\n\x10relativeStopLoss\x18\x14 \x01(\x03\x12\x1a\n\x12relativeTakeProfit\x18\x15 \x01(\x03\x12\x11\n\tisStopOut\x18\x16 \x01(\x08\x12\x18\n\x10trailingStopLoss\x18\x17 \x01(\x08\x12<\n\x11stopTriggerMethod\x18\x18 \x01(\x0e\x32\x1a.ProtoOAOrderTriggerMethod:\x05TRADE\"\x99\x02\n\x1bProtoOABonusDepositWithdraw\x12.\n\roperationType\x18\x01 \x02(\x0e\x32\x17.ProtoOAChangeBonusType\x12\x16\n\x0e\x62onusHistoryId\x18\x02 \x02(\x03\x12\x14\n\x0cmanagerBonus\x18\x03 \x02(\x03\x12\x14\n\x0cmanagerDelta\x18\x04 \x02(\x03\x12\x0f\n\x07ibBonus\x18\x05 \x02(\x03\x12\x0f\n\x07ibDelta\x18\x06 \x02(\x03\x12\x1c\n\x14\x63hangeBonusTimestamp\x18\x07 \x02(\x03\x12\x14\n\x0c\x65xternalNote\x18\x08 \x01(\t\x12\x1b\n\x13introducingBrokerId\x18\t \x01(\x03\x12\x13\n\x0bmoneyDigits\x18\n \x01(\r\"\xf7\x01\n\x16ProtoOADepositWithdraw\x12\x30\n\roperationType\x18\x01 \x02(\x0e\x32\x19.ProtoOAChangeBalanceType\x12\x18\n\x10\x62\x61lanceHistoryId\x18\x02 \x02(\x03\x12\x0f\n\x07\x62\x61lance\x18\x03 \x02(\x03\x12\r\n\x05\x64\x65lta\x18\x04 \x02(\x03\x12\x1e\n\x16\x63hangeBalanceTimestamp\x18\x05 \x02(\x03\x12\x14\n\x0c\x65xternalNote\x18\x06 \x01(\t\x12\x16\n\x0e\x62\x61lanceVersion\x18\x07 \x01(\x03\x12\x0e\n\x06\x65quity\x18\x08 \x01(\x03\x12\x13\n\x0bmoneyDigits\x18\t \x01(\r\"\xcd\x03\n\x0bProtoOADeal\x12\x0e\n\x06\x64\x65\x61lId\x18\x01 \x02(\x03\x12\x0f\n\x07orderId\x18\x02 \x02(\x03\x12\x12\n\npositionId\x18\x03 \x02(\x03\x12\x0e\n\x06volume\x18\x04 \x02(\x03\x12\x14\n\x0c\x66illedVolume\x18\x05 \x02(\x03\x12\x10\n\x08symbolId\x18\x06 \x02(\x03\x12\x17\n\x0f\x63reateTimestamp\x18\x07 \x02(\x03\x12\x1a\n\x12\x65xecutionTimestamp\x18\x08 \x02(\x03\x12\x1e\n\x16utcLastUpdateTimestamp\x18\t \x01(\x03\x12\x16\n\x0e\x65xecutionPrice\x18\n \x01(\x01\x12$\n\ttradeSide\x18\x0b \x02(\x0e\x32\x11.ProtoOATradeSide\x12&\n\ndealStatus\x18\x0c \x02(\x0e\x32\x12.ProtoOADealStatus\x12\x12\n\nmarginRate\x18\r \x01(\x01\x12\x12\n\ncommission\x18\x0e \x01(\x03\x12\x1f\n\x17\x62\x61seToUsdConversionRate\x18\x0f \x01(\x01\x12\x38\n\x13\x63losePositionDetail\x18\x10 \x01(\x0b\x32\x1b.ProtoOAClosePositionDetail\x12\x13\n\x0bmoneyDigits\x18\x11 \x01(\r\"\xfb\x01\n\x1aProtoOAClosePositionDetail\x12\x12\n\nentryPrice\x18\x01 \x02(\x01\x12\x13\n\x0bgrossProfit\x18\x02 \x02(\x03\x12\x0c\n\x04swap\x18\x03 \x02(\x03\x12\x12\n\ncommission\x18\x04 \x02(\x03\x12\x0f\n\x07\x62\x61lance\x18\x05 \x02(\x03\x12$\n\x1cquoteToDepositConversionRate\x18\x06 \x01(\x01\x12\x14\n\x0c\x63losedVolume\x18\x07 \x01(\x03\x12\x16\n\x0e\x62\x61lanceVersion\x18\x08 \x01(\x03\x12\x13\n\x0bmoneyDigits\x18\t \x01(\r\x12\x18\n\x10pnlConversionFee\x18\n \x01(\x03\"\xb3\x01\n\x0fProtoOATrendbar\x12\x0e\n\x06volume\x18\x03 \x02(\x03\x12*\n\x06period\x18\x04 \x01(\x0e\x32\x16.ProtoOATrendbarPeriod:\x02M1\x12\x0b\n\x03low\x18\x05 \x01(\x03\x12\x11\n\tdeltaOpen\x18\x06 \x01(\x04\x12\x12\n\ndeltaClose\x18\x07 \x01(\x04\x12\x11\n\tdeltaHigh\x18\x08 \x01(\x04\x12\x1d\n\x15utcTimestampInMinutes\x18\t \x01(\r\"N\n\x15ProtoOAExpectedMargin\x12\x0e\n\x06volume\x18\x01 \x02(\x03\x12\x11\n\tbuyMargin\x18\x02 \x02(\x03\x12\x12\n\nsellMargin\x18\x03 \x02(\x03\"2\n\x0fProtoOATickData\x12\x11\n\ttimestamp\x18\x01 \x02(\x03\x12\x0c\n\x04tick\x18\x02 \x02(\x03\"$\n\x12ProtoOACtidProfile\x12\x0e\n\x06userId\x18\x01 \x02(\x03\"\xa2\x01\n\x18ProtoOACtidTraderAccount\x12\x1b\n\x13\x63tidTraderAccountId\x18\x01 \x02(\x04\x12\x0e\n\x06isLive\x18\x02 \x01(\x08\x12\x13\n\x0btraderLogin\x18\x03 \x01(\x03\x12 \n\x18lastClosingDealTimestamp\x18\x04 \x01(\x03\x12\"\n\x1alastBalanceUpdateTimestamp\x18\x05 \x01(\x03\"-\n\x11ProtoOAAssetClass\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x0c\n\x04name\x18\x02 \x01(\t\"G\n\x11ProtoOADepthQuote\x12\n\n\x02id\x18\x01 \x02(\x04\x12\x0c\n\x04size\x18\x03 \x02(\x04\x12\x0b\n\x03\x62id\x18\x04 \x01(\x04\x12\x0b\n\x03\x61sk\x18\x05 \x01(\x04\"\x83\x01\n\x11ProtoOAMarginCall\x12\x30\n\x0emarginCallType\x18\x01 \x02(\x0e\x32\x18.ProtoOANotificationType\x12\x1c\n\x14marginLevelThreshold\x18\x02 \x02(\x01\x12\x1e\n\x16utcLastUpdateTimestamp\x18\x03 \x01(\x03\"\xb2\x01\n\x0eProtoOAHoliday\x12\x11\n\tholidayId\x18\x01 \x02(\x03\x12\x0c\n\x04name\x18\x02 \x02(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x18\n\x10scheduleTimeZone\x18\x04 \x02(\t\x12\x13\n\x0bholidayDate\x18\x05 \x02(\x03\x12\x13\n\x0bisRecurring\x18\x06 \x02(\x08\x12\x13\n\x0bstartSecond\x18\x07 \x01(\x05\x12\x11\n\tendSecond\x18\x08 \x01(\x05\"X\n\x16ProtoOADynamicLeverage\x12\x12\n\nleverageId\x18\x01 \x02(\x03\x12*\n\x05tiers\x18\x02 \x03(\x0b\x32\x1b.ProtoOADynamicLeverageTier\">\n\x1aProtoOADynamicLeverageTier\x12\x0e\n\x06volume\x18\x01 \x02(\x03\x12\x10\n\x08leverage\x18\x02 \x02(\x03\"g\n\x11ProtoOADealOffset\x12\x0e\n\x06\x64\x65\x61lId\x18\x01 \x02(\x03\x12\x0e\n\x06volume\x18\x02 \x02(\x03\x12\x1a\n\x12\x65xecutionTimestamp\x18\x03 \x01(\x03\x12\x16\n\x0e\x65xecutionPrice\x18\x04 \x01(\x01\"h\n\x1cProtoOAPositionUnrealizedPnL\x12\x12\n\npositionId\x18\x01 \x02(\x03\x12\x1a\n\x12grossUnrealizedPnL\x18\x02 \x02(\x03\x12\x18\n\x10netUnrealizedPnL\x18\x03 \x02(\x05*\x86\x1b\n\x12ProtoOAPayloadType\x12\"\n\x1dPROTO_OA_APPLICATION_AUTH_REQ\x10\xb4\x10\x12\"\n\x1dPROTO_OA_APPLICATION_AUTH_RES\x10\xb5\x10\x12\x1e\n\x19PROTO_OA_ACCOUNT_AUTH_REQ\x10\xb6\x10\x12\x1e\n\x19PROTO_OA_ACCOUNT_AUTH_RES\x10\xb7\x10\x12\x19\n\x14PROTO_OA_VERSION_REQ\x10\xb8\x10\x12\x19\n\x14PROTO_OA_VERSION_RES\x10\xb9\x10\x12\x1b\n\x16PROTO_OA_NEW_ORDER_REQ\x10\xba\x10\x12\'\n\"PROTO_OA_TRAILING_SL_CHANGED_EVENT\x10\xbb\x10\x12\x1e\n\x19PROTO_OA_CANCEL_ORDER_REQ\x10\xbc\x10\x12\x1d\n\x18PROTO_OA_AMEND_ORDER_REQ\x10\xbd\x10\x12%\n PROTO_OA_AMEND_POSITION_SLTP_REQ\x10\xbe\x10\x12 \n\x1bPROTO_OA_CLOSE_POSITION_REQ\x10\xbf\x10\x12\x1c\n\x17PROTO_OA_ASSET_LIST_REQ\x10\xc0\x10\x12\x1c\n\x17PROTO_OA_ASSET_LIST_RES\x10\xc1\x10\x12\x1e\n\x19PROTO_OA_SYMBOLS_LIST_REQ\x10\xc2\x10\x12\x1e\n\x19PROTO_OA_SYMBOLS_LIST_RES\x10\xc3\x10\x12\x1e\n\x19PROTO_OA_SYMBOL_BY_ID_REQ\x10\xc4\x10\x12\x1e\n\x19PROTO_OA_SYMBOL_BY_ID_RES\x10\xc5\x10\x12(\n#PROTO_OA_SYMBOLS_FOR_CONVERSION_REQ\x10\xc6\x10\x12(\n#PROTO_OA_SYMBOLS_FOR_CONVERSION_RES\x10\xc7\x10\x12\"\n\x1dPROTO_OA_SYMBOL_CHANGED_EVENT\x10\xc8\x10\x12\x18\n\x13PROTO_OA_TRADER_REQ\x10\xc9\x10\x12\x18\n\x13PROTO_OA_TRADER_RES\x10\xca\x10\x12!\n\x1cPROTO_OA_TRADER_UPDATE_EVENT\x10\xcb\x10\x12\x1b\n\x16PROTO_OA_RECONCILE_REQ\x10\xcc\x10\x12\x1b\n\x16PROTO_OA_RECONCILE_RES\x10\xcd\x10\x12\x1d\n\x18PROTO_OA_EXECUTION_EVENT\x10\xce\x10\x12!\n\x1cPROTO_OA_SUBSCRIBE_SPOTS_REQ\x10\xcf\x10\x12!\n\x1cPROTO_OA_SUBSCRIBE_SPOTS_RES\x10\xd0\x10\x12#\n\x1ePROTO_OA_UNSUBSCRIBE_SPOTS_REQ\x10\xd1\x10\x12#\n\x1ePROTO_OA_UNSUBSCRIBE_SPOTS_RES\x10\xd2\x10\x12\x18\n\x13PROTO_OA_SPOT_EVENT\x10\xd3\x10\x12\x1f\n\x1aPROTO_OA_ORDER_ERROR_EVENT\x10\xd4\x10\x12\x1b\n\x16PROTO_OA_DEAL_LIST_REQ\x10\xd5\x10\x12\x1b\n\x16PROTO_OA_DEAL_LIST_RES\x10\xd6\x10\x12)\n$PROTO_OA_SUBSCRIBE_LIVE_TRENDBAR_REQ\x10\xd7\x10\x12+\n&PROTO_OA_UNSUBSCRIBE_LIVE_TRENDBAR_REQ\x10\xd8\x10\x12\x1f\n\x1aPROTO_OA_GET_TRENDBARS_REQ\x10\xd9\x10\x12\x1f\n\x1aPROTO_OA_GET_TRENDBARS_RES\x10\xda\x10\x12!\n\x1cPROTO_OA_EXPECTED_MARGIN_REQ\x10\xdb\x10\x12!\n\x1cPROTO_OA_EXPECTED_MARGIN_RES\x10\xdc\x10\x12\"\n\x1dPROTO_OA_MARGIN_CHANGED_EVENT\x10\xdd\x10\x12\x17\n\x12PROTO_OA_ERROR_RES\x10\xde\x10\x12(\n#PROTO_OA_CASH_FLOW_HISTORY_LIST_REQ\x10\xdf\x10\x12(\n#PROTO_OA_CASH_FLOW_HISTORY_LIST_RES\x10\xe0\x10\x12\x1e\n\x19PROTO_OA_GET_TICKDATA_REQ\x10\xe1\x10\x12\x1e\n\x19PROTO_OA_GET_TICKDATA_RES\x10\xe2\x10\x12.\n)PROTO_OA_ACCOUNTS_TOKEN_INVALIDATED_EVENT\x10\xe3\x10\x12%\n PROTO_OA_CLIENT_DISCONNECT_EVENT\x10\xe4\x10\x12.\n)PROTO_OA_GET_ACCOUNTS_BY_ACCESS_TOKEN_REQ\x10\xe5\x10\x12.\n)PROTO_OA_GET_ACCOUNTS_BY_ACCESS_TOKEN_RES\x10\xe6\x10\x12+\n&PROTO_OA_GET_CTID_PROFILE_BY_TOKEN_REQ\x10\xe7\x10\x12+\n&PROTO_OA_GET_CTID_PROFILE_BY_TOKEN_RES\x10\xe8\x10\x12\"\n\x1dPROTO_OA_ASSET_CLASS_LIST_REQ\x10\xe9\x10\x12\"\n\x1dPROTO_OA_ASSET_CLASS_LIST_RES\x10\xea\x10\x12\x19\n\x14PROTO_OA_DEPTH_EVENT\x10\xeb\x10\x12(\n#PROTO_OA_SUBSCRIBE_DEPTH_QUOTES_REQ\x10\xec\x10\x12(\n#PROTO_OA_SUBSCRIBE_DEPTH_QUOTES_RES\x10\xed\x10\x12*\n%PROTO_OA_UNSUBSCRIBE_DEPTH_QUOTES_REQ\x10\xee\x10\x12*\n%PROTO_OA_UNSUBSCRIBE_DEPTH_QUOTES_RES\x10\xef\x10\x12!\n\x1cPROTO_OA_SYMBOL_CATEGORY_REQ\x10\xf0\x10\x12!\n\x1cPROTO_OA_SYMBOL_CATEGORY_RES\x10\xf1\x10\x12 \n\x1bPROTO_OA_ACCOUNT_LOGOUT_REQ\x10\xf2\x10\x12 \n\x1bPROTO_OA_ACCOUNT_LOGOUT_RES\x10\xf3\x10\x12&\n!PROTO_OA_ACCOUNT_DISCONNECT_EVENT\x10\xf4\x10\x12)\n$PROTO_OA_SUBSCRIBE_LIVE_TRENDBAR_RES\x10\xf5\x10\x12+\n&PROTO_OA_UNSUBSCRIBE_LIVE_TRENDBAR_RES\x10\xf6\x10\x12\"\n\x1dPROTO_OA_MARGIN_CALL_LIST_REQ\x10\xf7\x10\x12\"\n\x1dPROTO_OA_MARGIN_CALL_LIST_RES\x10\xf8\x10\x12$\n\x1fPROTO_OA_MARGIN_CALL_UPDATE_REQ\x10\xf9\x10\x12$\n\x1fPROTO_OA_MARGIN_CALL_UPDATE_RES\x10\xfa\x10\x12&\n!PROTO_OA_MARGIN_CALL_UPDATE_EVENT\x10\xfb\x10\x12\'\n\"PROTO_OA_MARGIN_CALL_TRIGGER_EVENT\x10\xfc\x10\x12\x1f\n\x1aPROTO_OA_REFRESH_TOKEN_REQ\x10\xfd\x10\x12\x1f\n\x1aPROTO_OA_REFRESH_TOKEN_RES\x10\xfe\x10\x12\x1c\n\x17PROTO_OA_ORDER_LIST_REQ\x10\xff\x10\x12\x1c\n\x17PROTO_OA_ORDER_LIST_RES\x10\x80\x11\x12&\n!PROTO_OA_GET_DYNAMIC_LEVERAGE_REQ\x10\x81\x11\x12&\n!PROTO_OA_GET_DYNAMIC_LEVERAGE_RES\x10\x82\x11\x12*\n%PROTO_OA_DEAL_LIST_BY_POSITION_ID_REQ\x10\x83\x11\x12*\n%PROTO_OA_DEAL_LIST_BY_POSITION_ID_RES\x10\x84\x11\x12\x1f\n\x1aPROTO_OA_ORDER_DETAILS_REQ\x10\x85\x11\x12\x1f\n\x1aPROTO_OA_ORDER_DETAILS_RES\x10\x86\x11\x12+\n&PROTO_OA_ORDER_LIST_BY_POSITION_ID_REQ\x10\x87\x11\x12+\n&PROTO_OA_ORDER_LIST_BY_POSITION_ID_RES\x10\x88\x11\x12\"\n\x1dPROTO_OA_DEAL_OFFSET_LIST_REQ\x10\x89\x11\x12\"\n\x1dPROTO_OA_DEAL_OFFSET_LIST_RES\x10\x8a\x11\x12-\n(PROTO_OA_GET_POSITION_UNREALIZED_PNL_REQ\x10\x8b\x11\x12-\n(PROTO_OA_GET_POSITION_UNREALIZED_PNL_RES\x10\x8c\x11\x12!\n\x1cPROTO_OA_V1_PNL_CHANGE_EVENT\x10\x8d\x11\x12)\n$PROTO_OA_V1_PNL_CHANGE_SUBSCRIBE_REQ\x10\x8e\x11\x12)\n$PROTO_OA_V1_PNL_CHANGE_SUBSCRIBE_RES\x10\x8f\x11\x12,\n\'PROTO_OA_V1_PNL_CHANGE_UN_SUBSCRIBE_REQ\x10\x90\x11\x12,\n\'PROTO_OA_V1_PNL_CHANGE_UN_SUBSCRIBE_RES\x10\x91\x11*x\n\x10ProtoOADayOfWeek\x12\x08\n\x04NONE\x10\x00\x12\n\n\x06MONDAY\x10\x01\x12\x0b\n\x07TUESDAY\x10\x02\x12\r\n\tWEDNESDAY\x10\x03\x12\x0c\n\x08THURSDAY\x10\x04\x12\n\n\x06\x46RIDAY\x10\x05\x12\x0c\n\x08SATURDAY\x10\x06\x12\n\n\x06SUNDAY\x10\x07*q\n\x15ProtoOACommissionType\x12\x17\n\x13USD_PER_MILLION_USD\x10\x01\x12\x0f\n\x0bUSD_PER_LOT\x10\x02\x12\x17\n\x13PERCENTAGE_OF_VALUE\x10\x03\x12\x15\n\x11QUOTE_CCY_PER_LOT\x10\x04*]\n\x19ProtoOASymbolDistanceType\x12\x1d\n\x19SYMBOL_DISTANCE_IN_POINTS\x10\x01\x12!\n\x1dSYMBOL_DISTANCE_IN_PERCENTAGE\x10\x02*<\n\x18ProtoOAMinCommissionType\x12\x0c\n\x08\x43URRENCY\x10\x01\x12\x12\n\x0eQUOTE_CURRENCY\x10\x02*\x85\x01\n\x12ProtoOATradingMode\x12\x0b\n\x07\x45NABLED\x10\x00\x12\'\n#DISABLED_WITHOUT_PENDINGS_EXECUTION\x10\x01\x12$\n DISABLED_WITH_PENDINGS_EXECUTION\x10\x02\x12\x13\n\x0f\x43LOSE_ONLY_MODE\x10\x03*6\n\x1aProtoOASwapCalculationType\x12\x08\n\x04PIPS\x10\x00\x12\x0e\n\nPERCENTAGE\x10\x01*T\n\x13ProtoOAAccessRights\x12\x0f\n\x0b\x46ULL_ACCESS\x10\x00\x12\x0e\n\nCLOSE_ONLY\x10\x01\x12\x0e\n\nNO_TRADING\x10\x02\x12\x0c\n\x08NO_LOGIN\x10\x03*>\n!ProtoOATotalMarginCalculationType\x12\x07\n\x03MAX\x10\x00\x12\x07\n\x03SUM\x10\x01\x12\x07\n\x03NET\x10\x02*@\n\x12ProtoOAAccountType\x12\n\n\x06HEDGED\x10\x00\x12\n\n\x06NETTED\x10\x01\x12\x12\n\x0eSPREAD_BETTING\x10\x02*\x85\x01\n\x15ProtoOAPositionStatus\x12\x18\n\x14POSITION_STATUS_OPEN\x10\x01\x12\x1a\n\x16POSITION_STATUS_CLOSED\x10\x02\x12\x1b\n\x17POSITION_STATUS_CREATED\x10\x03\x12\x19\n\x15POSITION_STATUS_ERROR\x10\x04*%\n\x10ProtoOATradeSide\x12\x07\n\x03\x42UY\x10\x01\x12\x08\n\x04SELL\x10\x02*p\n\x10ProtoOAOrderType\x12\n\n\x06MARKET\x10\x01\x12\t\n\x05LIMIT\x10\x02\x12\x08\n\x04STOP\x10\x03\x12\x19\n\x15STOP_LOSS_TAKE_PROFIT\x10\x04\x12\x10\n\x0cMARKET_RANGE\x10\x05\x12\x0e\n\nSTOP_LIMIT\x10\x06*}\n\x12ProtoOATimeInForce\x12\x12\n\x0eGOOD_TILL_DATE\x10\x01\x12\x14\n\x10GOOD_TILL_CANCEL\x10\x02\x12\x17\n\x13IMMEDIATE_OR_CANCEL\x10\x03\x12\x10\n\x0c\x46ILL_OR_KILL\x10\x04\x12\x12\n\x0eMARKET_ON_OPEN\x10\x05*\x99\x01\n\x12ProtoOAOrderStatus\x12\x19\n\x15ORDER_STATUS_ACCEPTED\x10\x01\x12\x17\n\x13ORDER_STATUS_FILLED\x10\x02\x12\x19\n\x15ORDER_STATUS_REJECTED\x10\x03\x12\x18\n\x14ORDER_STATUS_EXPIRED\x10\x04\x12\x1a\n\x16ORDER_STATUS_CANCELLED\x10\x05*[\n\x19ProtoOAOrderTriggerMethod\x12\t\n\x05TRADE\x10\x01\x12\x0c\n\x08OPPOSITE\x10\x02\x12\x10\n\x0c\x44OUBLE_TRADE\x10\x03\x12\x13\n\x0f\x44OUBLE_OPPOSITE\x10\x04*\xfb\x01\n\x14ProtoOAExecutionType\x12\x12\n\x0eORDER_ACCEPTED\x10\x02\x12\x10\n\x0cORDER_FILLED\x10\x03\x12\x12\n\x0eORDER_REPLACED\x10\x04\x12\x13\n\x0fORDER_CANCELLED\x10\x05\x12\x11\n\rORDER_EXPIRED\x10\x06\x12\x12\n\x0eORDER_REJECTED\x10\x07\x12\x19\n\x15ORDER_CANCEL_REJECTED\x10\x08\x12\x08\n\x04SWAP\x10\t\x12\x14\n\x10\x44\x45POSIT_WITHDRAW\x10\n\x12\x16\n\x12ORDER_PARTIAL_FILL\x10\x0b\x12\x1a\n\x16\x42ONUS_DEPOSIT_WITHDRAW\x10\x0c*?\n\x16ProtoOAChangeBonusType\x12\x11\n\rBONUS_DEPOSIT\x10\x00\x12\x12\n\x0e\x42ONUS_WITHDRAW\x10\x01*\xb8\n\n\x18ProtoOAChangeBalanceType\x12\x13\n\x0f\x42\x41LANCE_DEPOSIT\x10\x00\x12\x14\n\x10\x42\x41LANCE_WITHDRAW\x10\x01\x12-\n)BALANCE_DEPOSIT_STRATEGY_COMMISSION_INNER\x10\x03\x12.\n*BALANCE_WITHDRAW_STRATEGY_COMMISSION_INNER\x10\x04\x12\"\n\x1e\x42\x41LANCE_DEPOSIT_IB_COMMISSIONS\x10\x05\x12)\n%BALANCE_WITHDRAW_IB_SHARED_PERCENTAGE\x10\x06\x12\x34\n0BALANCE_DEPOSIT_IB_SHARED_PERCENTAGE_FROM_SUB_IB\x10\x07\x12\x34\n0BALANCE_DEPOSIT_IB_SHARED_PERCENTAGE_FROM_BROKER\x10\x08\x12\x1a\n\x16\x42\x41LANCE_DEPOSIT_REBATE\x10\t\x12\x1b\n\x17\x42\x41LANCE_WITHDRAW_REBATE\x10\n\x12-\n)BALANCE_DEPOSIT_STRATEGY_COMMISSION_OUTER\x10\x0b\x12.\n*BALANCE_WITHDRAW_STRATEGY_COMMISSION_OUTER\x10\x0c\x12\'\n#BALANCE_WITHDRAW_BONUS_COMPENSATION\x10\r\x12\x33\n/BALANCE_WITHDRAW_IB_SHARED_PERCENTAGE_TO_BROKER\x10\x0e\x12\x1d\n\x19\x42\x41LANCE_DEPOSIT_DIVIDENDS\x10\x0f\x12\x1e\n\x1a\x42\x41LANCE_WITHDRAW_DIVIDENDS\x10\x10\x12\x1f\n\x1b\x42\x41LANCE_WITHDRAW_GSL_CHARGE\x10\x11\x12\x1d\n\x19\x42\x41LANCE_WITHDRAW_ROLLOVER\x10\x12\x12)\n%BALANCE_DEPOSIT_NONWITHDRAWABLE_BONUS\x10\x13\x12*\n&BALANCE_WITHDRAW_NONWITHDRAWABLE_BONUS\x10\x14\x12\x18\n\x14\x42\x41LANCE_DEPOSIT_SWAP\x10\x15\x12\x19\n\x15\x42\x41LANCE_WITHDRAW_SWAP\x10\x16\x12\"\n\x1e\x42\x41LANCE_DEPOSIT_MANAGEMENT_FEE\x10\x1b\x12#\n\x1f\x42\x41LANCE_WITHDRAW_MANAGEMENT_FEE\x10\x1c\x12#\n\x1f\x42\x41LANCE_DEPOSIT_PERFORMANCE_FEE\x10\x1d\x12#\n\x1f\x42\x41LANCE_WITHDRAW_FOR_SUBACCOUNT\x10\x1e\x12!\n\x1d\x42\x41LANCE_DEPOSIT_TO_SUBACCOUNT\x10\x1f\x12$\n BALANCE_WITHDRAW_FROM_SUBACCOUNT\x10 \x12#\n\x1f\x42\x41LANCE_DEPOSIT_FROM_SUBACCOUNT\x10!\x12\x1d\n\x19\x42\x41LANCE_WITHDRAW_COPY_FEE\x10\"\x12#\n\x1f\x42\x41LANCE_WITHDRAW_INACTIVITY_FEE\x10#\x12\x1c\n\x18\x42\x41LANCE_DEPOSIT_TRANSFER\x10$\x12\x1d\n\x19\x42\x41LANCE_WITHDRAW_TRANSFER\x10%\x12#\n\x1f\x42\x41LANCE_DEPOSIT_CONVERTED_BONUS\x10&\x12/\n+BALANCE_DEPOSIT_NEGATIVE_BALANCE_PROTECTION\x10\'*s\n\x11ProtoOADealStatus\x12\n\n\x06\x46ILLED\x10\x02\x12\x14\n\x10PARTIALLY_FILLED\x10\x03\x12\x0c\n\x08REJECTED\x10\x04\x12\x17\n\x13INTERNALLY_REJECTED\x10\x05\x12\t\n\x05\x45RROR\x10\x06\x12\n\n\x06MISSED\x10\x07*\x8c\x01\n\x15ProtoOATrendbarPeriod\x12\x06\n\x02M1\x10\x01\x12\x06\n\x02M2\x10\x02\x12\x06\n\x02M3\x10\x03\x12\x06\n\x02M4\x10\x04\x12\x06\n\x02M5\x10\x05\x12\x07\n\x03M10\x10\x06\x12\x07\n\x03M15\x10\x07\x12\x07\n\x03M30\x10\x08\x12\x06\n\x02H1\x10\t\x12\x06\n\x02H4\x10\n\x12\x07\n\x03H12\x10\x0b\x12\x06\n\x02\x44\x31\x10\x0c\x12\x06\n\x02W1\x10\r\x12\x07\n\x03MN1\x10\x0e*$\n\x10ProtoOAQuoteType\x12\x07\n\x03\x42ID\x10\x01\x12\x07\n\x03\x41SK\x10\x02*K\n\x16ProtoOAStopOutStrategy\x12\x1a\n\x16MOST_MARGIN_USED_FIRST\x10\x00\x12\x15\n\x11MOST_LOSING_FIRST\x10\x01*?\n\x1cProtoOAClientPermissionScope\x12\x0e\n\nSCOPE_VIEW\x10\x00\x12\x0f\n\x0bSCOPE_TRADE\x10\x01*s\n\x17ProtoOANotificationType\x12\x1c\n\x18MARGIN_LEVEL_THRESHOLD_1\x10=\x12\x1c\n\x18MARGIN_LEVEL_THRESHOLD_2\x10>\x12\x1c\n\x18MARGIN_LEVEL_THRESHOLD_3\x10?*\xde\x08\n\x10ProtoOAErrorCode\x12\x19\n\x15OA_AUTH_TOKEN_EXPIRED\x10\x01\x12\x1a\n\x16\x41\x43\x43OUNT_NOT_AUTHORIZED\x10\x02\x12\x15\n\x11\x41LREADY_LOGGED_IN\x10\x0e\x12\x1a\n\x16\x43H_CLIENT_AUTH_FAILURE\x10\x65\x12\x1f\n\x1b\x43H_CLIENT_NOT_AUTHENTICATED\x10\x66\x12#\n\x1f\x43H_CLIENT_ALREADY_AUTHENTICATED\x10g\x12\x1b\n\x17\x43H_ACCESS_TOKEN_INVALID\x10h\x12\x1b\n\x17\x43H_SERVER_NOT_REACHABLE\x10i\x12$\n CH_CTID_TRADER_ACCOUNT_NOT_FOUND\x10j\x12\x1a\n\x16\x43H_OA_CLIENT_NOT_FOUND\x10k\x12\x1e\n\x1aREQUEST_FREQUENCY_EXCEEDED\x10l\x12\x1f\n\x1bSERVER_IS_UNDER_MAINTENANCE\x10m\x12\x16\n\x12\x43HANNEL_IS_BLOCKED\x10n\x12\x1e\n\x1a\x43ONNECTIONS_LIMIT_EXCEEDED\x10\x43\x12\x19\n\x15WORSE_GSL_NOT_ALLOWED\x10\x44\x12\x16\n\x12SYMBOL_HAS_HOLIDAY\x10\x45\x12\x1b\n\x17NOT_SUBSCRIBED_TO_SPOTS\x10p\x12\x16\n\x12\x41LREADY_SUBSCRIBED\x10q\x12\x14\n\x10SYMBOL_NOT_FOUND\x10r\x12\x12\n\x0eUNKNOWN_SYMBOL\x10s\x12\x18\n\x14INCORRECT_BOUNDARIES\x10#\x12\r\n\tNO_QUOTES\x10u\x12\x14\n\x10NOT_ENOUGH_MONEY\x10v\x12\x18\n\x14MAX_EXPOSURE_REACHED\x10w\x12\x16\n\x12POSITION_NOT_FOUND\x10x\x12\x13\n\x0fORDER_NOT_FOUND\x10y\x12\x15\n\x11POSITION_NOT_OPEN\x10z\x12\x13\n\x0fPOSITION_LOCKED\x10{\x12\x16\n\x12TOO_MANY_POSITIONS\x10|\x12\x16\n\x12TRADING_BAD_VOLUME\x10}\x12\x15\n\x11TRADING_BAD_STOPS\x10~\x12\x16\n\x12TRADING_BAD_PRICES\x10\x7f\x12\x16\n\x11TRADING_BAD_STAKE\x10\x80\x01\x12&\n!PROTECTION_IS_TOO_CLOSE_TO_MARKET\x10\x81\x01\x12 \n\x1bTRADING_BAD_EXPIRATION_DATE\x10\x82\x01\x12\x16\n\x11PENDING_EXECUTION\x10\x83\x01\x12\x15\n\x10TRADING_DISABLED\x10\x84\x01\x12\x18\n\x13TRADING_NOT_ALLOWED\x10\x85\x01\x12\x1b\n\x16UNABLE_TO_CANCEL_ORDER\x10\x86\x01\x12\x1a\n\x15UNABLE_TO_AMEND_ORDER\x10\x87\x01\x12\x1e\n\x19SHORT_SELLING_NOT_ALLOWED\x10\x88\x01*\x81\x01\n+ProtoOALimitedRiskMarginCalculationStrategy\x12\x19\n\x15\x41\x43\x43ORDING_TO_LEVERAGE\x10\x00\x12\x14\n\x10\x41\x43\x43ORDING_TO_GSL\x10\x01\x12!\n\x1d\x41\x43\x43ORDING_TO_GSL_AND_LEVERAGE\x10\x02\x42M\n%com.xtrader.protocol.openapi.v2.modelB\x1f\x43ontainerOpenApiV2ModelMessagesP\x01\xa0\x01\x01')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'OpenApiModelMessages_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n%com.xtrader.protocol.openapi.v2.modelB\037ContainerOpenApiV2ModelMessagesP\001\240\001\001'
  _PROTOOASYMBOL.fields_by_name['commission']._options = None
  _PROTOOASYMBOL.fields_by_name['commission']._serialized_options = b'\030\001'
  _PROTOOASYMBOL.fields_by_name['minCommission']._options = None
  _PROTOOASYMBOL.fields_by_name['minCommission']._serialized_options = b'\030\001'
  _PROTOOATRADER.fields_by_name['frenchRisk']._options = None
  _PROTOOATRADER.fields_by_name['frenchRisk']._serialized_options = b'\030\001'
  _PROTOOAPAYLOADTYPE._serialized_start=6100
  _PROTOOAPAYLOADTYPE._serialized_end = 9562
  _PROTOOADAYOFWEEK._serialized_start = 9564
  _PROTOOADAYOFWEEK._serialized_end = 9684
  _PROTOOACOMMISSIONTYPE._serialized_start = 9686
  _PROTOOACOMMISSIONTYPE._serialized_end = 9799
  _PROTOOASYMBOLDISTANCETYPE._serialized_start = 9801
  _PROTOOASYMBOLDISTANCETYPE._serialized_end = 9894
  _PROTOOAMINCOMMISSIONTYPE._serialized_start = 9896
  _PROTOOAMINCOMMISSIONTYPE._serialized_end = 9956
  _PROTOOATRADINGMODE._serialized_start = 9959
  _PROTOOATRADINGMODE._serialized_end = 10092
  _PROTOOASWAPCALCULATIONTYPE._serialized_start = 10094
  _PROTOOASWAPCALCULATIONTYPE._serialized_end = 10148
  _PROTOOAACCESSRIGHTS._serialized_start = 10150
  _PROTOOAACCESSRIGHTS._serialized_end = 10234
  _PROTOOATOTALMARGINCALCULATIONTYPE._serialized_start = 10236
  _PROTOOATOTALMARGINCALCULATIONTYPE._serialized_end = 10298
  _PROTOOAACCOUNTTYPE._serialized_start = 10300
  _PROTOOAACCOUNTTYPE._serialized_end = 10364
  _PROTOOAPOSITIONSTATUS._serialized_start = 10367
  _PROTOOAPOSITIONSTATUS._serialized_end = 10500
  _PROTOOATRADESIDE._serialized_start = 10502
  _PROTOOATRADESIDE._serialized_end = 10539
  _PROTOOAORDERTYPE._serialized_start = 10541
  _PROTOOAORDERTYPE._serialized_end = 10653
  _PROTOOATIMEINFORCE._serialized_start = 10655
  _PROTOOATIMEINFORCE._serialized_end = 10780
  _PROTOOAORDERSTATUS._serialized_start = 10783
  _PROTOOAORDERSTATUS._serialized_end = 10936
  _PROTOOAORDERTRIGGERMETHOD._serialized_start = 10938
  _PROTOOAORDERTRIGGERMETHOD._serialized_end = 11029
  _PROTOOAEXECUTIONTYPE._serialized_start = 11032
  _PROTOOAEXECUTIONTYPE._serialized_end = 11283
  _PROTOOACHANGEBONUSTYPE._serialized_start = 11285
  _PROTOOACHANGEBONUSTYPE._serialized_end = 11348
  _PROTOOACHANGEBALANCETYPE._serialized_start = 11351
  _PROTOOACHANGEBALANCETYPE._serialized_end = 12687
  _PROTOOADEALSTATUS._serialized_start = 12689
  _PROTOOADEALSTATUS._serialized_end = 12804
  _PROTOOATRENDBARPERIOD._serialized_start = 12807
  _PROTOOATRENDBARPERIOD._serialized_end = 12947
  _PROTOOAQUOTETYPE._serialized_start = 12949
  _PROTOOAQUOTETYPE._serialized_end = 12985
  _PROTOOASTOPOUTSTRATEGY._serialized_start = 12987
  _PROTOOASTOPOUTSTRATEGY._serialized_end = 13062
  _PROTOOACLIENTPERMISSIONSCOPE._serialized_start = 13064
  _PROTOOACLIENTPERMISSIONSCOPE._serialized_end = 13127
  _PROTOOANOTIFICATIONTYPE._serialized_start = 13129
  _PROTOOANOTIFICATIONTYPE._serialized_end = 13244
  _PROTOOAERRORCODE._serialized_start = 13247
  _PROTOOAERRORCODE._serialized_end = 14365
  _PROTOOALIMITEDRISKMARGINCALCULATIONSTRATEGY._serialized_start = 14368
  _PROTOOALIMITEDRISKMARGINCALCULATIONSTRATEGY._serialized_end = 14497
  _PROTOOAASSET._serialized_start=30
  _PROTOOAASSET._serialized_end=112
  _PROTOOASYMBOL._serialized_start=115
  _PROTOOASYMBOL._serialized_end=1339
  _PROTOOALIGHTSYMBOL._serialized_start=1342
  _PROTOOALIGHTSYMBOL._serialized_end=1507
  _PROTOOAARCHIVEDSYMBOL._serialized_start=1509
  _PROTOOAARCHIVEDSYMBOL._serialized_end=1617
  _PROTOOASYMBOLCATEGORY._serialized_start=1619
  _PROTOOASYMBOLCATEGORY._serialized_end=1690
  _PROTOOAINTERVAL._serialized_start=1692
  _PROTOOAINTERVAL._serialized_end=1749
  _PROTOOATRADER._serialized_start=1752
  _PROTOOATRADER._serialized_end=2428
  _PROTOOAPOSITION._serialized_start=2431
  _PROTOOAPOSITION._serialized_end=2883
  _PROTOOATRADEDATA._serialized_start=2886
  _PROTOOATRADEDATA._serialized_end=3059
  _PROTOOAORDER._serialized_start=3062
  _PROTOOAORDER._serialized_end=3739
  _PROTOOABONUSDEPOSITWITHDRAW._serialized_start=3742
  _PROTOOABONUSDEPOSITWITHDRAW._serialized_end=4023
  _PROTOOADEPOSITWITHDRAW._serialized_start=4026
  _PROTOOADEPOSITWITHDRAW._serialized_end=4273
  _PROTOOADEAL._serialized_start=4276
  _PROTOOADEAL._serialized_end=4737
  _PROTOOACLOSEPOSITIONDETAIL._serialized_start=4740
  _PROTOOACLOSEPOSITIONDETAIL._serialized_end=4991
  _PROTOOATRENDBAR._serialized_start=4994
  _PROTOOATRENDBAR._serialized_end=5173
  _PROTOOAEXPECTEDMARGIN._serialized_start=5175
  _PROTOOAEXPECTEDMARGIN._serialized_end=5253
  _PROTOOATICKDATA._serialized_start=5255
  _PROTOOATICKDATA._serialized_end=5305
  _PROTOOACTIDPROFILE._serialized_start=5307
  _PROTOOACTIDPROFILE._serialized_end=5343
  _PROTOOACTIDTRADERACCOUNT._serialized_start=5346
  _PROTOOACTIDTRADERACCOUNT._serialized_end=5508
  _PROTOOAASSETCLASS._serialized_start=5510
  _PROTOOAASSETCLASS._serialized_end=5555
  _PROTOOADEPTHQUOTE._serialized_start=5557
  _PROTOOADEPTHQUOTE._serialized_end=5628
  _PROTOOAMARGINCALL._serialized_start=5631
  _PROTOOAMARGINCALL._serialized_end=5762
  _PROTOOAHOLIDAY._serialized_start=5765
  _PROTOOAHOLIDAY._serialized_end=5943
  _PROTOOADYNAMICLEVERAGE._serialized_start=5945
  _PROTOOADYNAMICLEVERAGE._serialized_end=6033
  _PROTOOADYNAMICLEVERAGETIER._serialized_start=6035
  _PROTOOADYNAMICLEVERAGETIER._serialized_end=6097
# @@protoc_insertion_point(module_scope)
