import requests
import hmac
import hashlib
import base64
import time

token = "YOUR TOKEN"
secretKey = b"YOUR SECRETKEY"

baseURL = "https://api.binance.com"
pingURL = "/api/v1/ping"
timeURL = "/api/v1/time"
bookURL = "/api/v1/depth"
recentTradeURL = "/api/v1/trades"
historicalTradeURL = "/api/v1/historicalTrades"
rangeTradeURL = "/api/v1/aggTrades"
candlestickURL = "/api/v1/klines"
dayURL="/api/v1/ticker/24hr"
priceURL = "/api/v3/ticker/price"
bookTickerURL="/api/v3/ticker/bookTicker"
testNewOrderURL = "/api/v3/order/test"
orderURL="/api/v3/order"
openOrdersURL="/api/v3/openOrders"
allOrdersURL="/api/v3/allOrders"
accountInfoURL="/api/v3/account"
accountTradesURL="/api/v3/myTrades"

######API CALLS

def getSignature(message, key):
	#returns a signature
	dig = hmac.new(key, msg=message, digestmod=hashlib.sha256).hexdigest()
	return dig

def checkStatus():
	#returns true if status=200, otherwise false
	global baseURL, pingURL
	if requests.get(baseURL+pingURL).status_code==200:
		return True 
	else:
		return False 

def getTimestamp():
	#returns timestamp of binance servers
	global baseURL, timeURL
	return requests.get(baseURL+timeURL).json()['serverTime']

def getOrderBook(symbol, limit=None):
	#returns current order book
	global baseURL, bookURL
	return requests.get(baseURL+bookURL, params={"symbol":symbol,"limit":limit}).json()

def getRecentTrades(symbol, limit=None):
	#returns recent trades
	global baseURL, recentTradeURL
	return requests.get(baseURL+recentTradeURL, params={"symbol":symbol, "limit":limit}).json()

def getHistoricalTrade(token, symbol, limit=None, fromId=None):
	#returns historical trade
	global baseURL, historicalTradeURL
	return requests.get(baseURL+historicalTradeURL, headers={"X-MBX-APIKEY":token},params={"symbol":symbol, "limit":limit, "fromId":fromId}).json()

def getTradesByTimeRange(token, symbol, startTime=None, endTime=None, limit=None, fromId=None):
	#returns trades in a timeframe
	global baseURL, rangeTradeURL
	return requests.get(baseURL+rangeTradeURL,headers={"X-MBX-APIKEY":token}, params={"symbol":symbol, "limit":limit, "fromId":fromId, "startTime":startTime, "endTime":endTime}).json()

def getCandleStick(token, symbol, interval, limit=None, startTime=None, endTime=None):
	#returns candlestick data
	#interval values can be:
	# "1m","3m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d","3d","1w", "1M"
	global baseURL, candlestickURL
	return requests.get(baseURL+candlestickURL, headers={"X-MBX-APIKEY":token},params={"symbol":symbol, "limit":limit, "interval":interval, "startTime":startTime, "endTime":endTime}).json()

def get24HrSwing(token, symbol=None):
	#returns 24hr data
	global baseURL, dayURL
	return requests.get(baseURL+dayURL, headers={"X-MBX-APIKEY":token},params={"symbol":symbol}).json()

def getPrice(token, symbol=None):
	#returns price data
	global baseURL, priceURL
	return requests.get(baseURL+priceURL, headers={"X-MBX-APIKEY":token},params={"symbol":symbol}).json()

def getBookTicker(token, symbol=None):
	#returns price/qty data
	global baseURL, bookTickerURL
	return requests.get(baseURL+bookTickerURL, headers={"X-MBX-APIKEY":token},params={"symbol":symbol}).json()

def newOrder(token, secretKey, symbol, side, orderType, quantity, timestamp=getTimestamp(), timeInForce=None, price=None, newClientOrderId=None, stopPrice=None, newOrderRespType=None, recvWindow=None, live=False):
	#submits a new order
	global baseURL, testNewOrderURL, orderURL
	if live != True:
		orderURL = testNewOrderURL
	data = {
			"symbol":symbol, 
			"side":side, 
			"type":orderType, 
			"quantity":quantity, 
			"timestamp":timestamp, 
			}
	message = "symbol={0}&side={1}&type={2}&quantity={3}&timestamp={4}".format(symbol, side, orderType, quantity, timestamp)
	if timeInForce != None:
		message+="&timeInForce={}".format(timeInForce)
		data['timeInForce']=timeInForce
	if price != None:
		message+="&price={}".format(price)
		data['price']=price
	if newClientOrderId != None:
		message+="&newClientOrderId={}".format(newClientOrderId)
		data['newClientOrderId']=newClientOrderId
	if stopPrice != None:
		message+="&stopPrice={}".format(stopPrice)
		data['stopPrice']=stopPrice
	if newOrderRespType!=None:
		message+="&newOrderRespType={}".format(newOrderRespType)
		data['newOrderRespType']=newOrderRespType
	if recvWindow!=None:
		message+="&recvWindow={}".format(recvWindow)
		data['recvWindow']=recvWindow
	signature = getSignature(message.encode('utf-8'), secretKey)
	data['signature']=signature
	return requests.post(baseURL+orderURL, headers={"X-MBX-APIKEY":token}, data=data).json()

def getOrderStatus(token, secretKey, symbol, timestamp=getTimestamp(), orderId=None, origClientId=None, recvWindow=None):
	#returns an order status
	global baseURL, orderURL
	message="symbol={0}&timestamp={1}".format(symbol, timestamp)
	params={
		"symbol":symbol,
		"timestamp":timestamp,
	}
	if orderId:
		params['orderId']=orderId
		message+="&orderId={}".format(orderId)
	if origClientId:
		params['origClientId']=origClientId
		message+="&origClientId={}".format(origClientId)
	if recvWindow:
		params['recvWindow']=recvWindow
		message+="&recvWindow={}".format(recvWindow)
	signature = getSignature(message.encode('utf-8'), secretKey)
	params['signature']=signature
	return requests.get(baseURL+orderURL, headers={"X-MBX-APIKEY":token}, params=params).json()

def cancelOrder(token, secretKey, symbol, timestamp=getTimestamp(), orderId=None, origClientId=None, newClientOrderId=None, recvWindow=None):
	#cancels an order
	global baseURL, orderURL
	message="symbol={0}&timestamp={1}".format(symbol, timestamp)
	params={
		"symbol":symbol,
		"timestamp":timestamp,
	}
	if orderId:
		params['orderId']=orderId
		message+="&orderId={}".format(orderId)
	if origClientId:
		params['origClientId']=origClientId
		message+="&origClientId={}".format(origClientId)
	if recvWindow:
		params['recvWindow']=recvWindow
		message+="&recvWindow={}".format(recvWindow)
	if newClientOrderId:
		params['newClientOrderId']=newClientOrderId
		message+="&newClientOrderId={}".format(newClientOrderId)
	signature = getSignature(message.encode('utf-8'), secretKey)
	params['signature']=signature
	return requests.delete(baseURL+orderURL,headers={"X-MBX-APIKEY":token}, params=params).json()

def getOpenOrders(token, secretKey, timestamp=getTimestamp(), symbol=None, recvWindow=None):
	#gets open orders
	global baseURL, openOrdersURL
	message = "timestamp={}".format(timestamp)
	params={
		"timestamp":timestamp
	}
	if symbol:
		params['symbol']=symbol
		message+="&symbol={}".format(symbol)
	if recvWindow:
		params['recvWindow']=recvWindow
		message+="&recvWindow=&{}".format(recvWindow)
	signature = getSignature(message.encode('utf-8'), secretKey)
	params['signature']=signature
	return requests.get(baseURL+openOrdersURL, headers={"X-MBX-APIKEY":token}, params=params).json()

def getAllOrders(token, secretKey, symbol, timestamp=getTimestamp(), recvWindow=None, limit=None, orderId=None):
	#returns all orders
	global baseURL, allOrdersURL
	message="symbol={0}&timestamp={1}".format(symbol, timestamp)
	params={
		"symbol":symbol,
		"timestamp":timestamp,
	}
	if orderId:
		params['orderId']=orderId
		message+="&orderId={}".format(orderId)
	if limit:
		params['limit']=limit
		message+="&limit={}".format(limit)
	if recvWindow:
		params['recvWindow']=recvWindow
		message+="&recvWindow={}".format(recvWindow)
	signature = getSignature(message.encode('utf-8'), secretKey)
	params['signature']=signature
	return requests.get(baseURL+allOrdersURL, headers={"X-MBX-APIKEY":token}, params=params).json()

def getAccountInfo(token, secretKey, timestamp=getTimestamp(), recvWindow=None):
	#gets account info
	global baseURL, accountInfoURL
	message="timestamp={}".format(timestamp)
	params={
		"timestamp":timestamp
	}
	if recvWindow:
		params['recvWindow']=recvWindow
		message+="&recvWindow={}".format(recvWindow)
	signature = getSignature(message.encode('utf-8'), secretKey)
	params['signature']=signature
	return requests.get(baseURL+accountInfoURL, headers={"X-MBX-APIKEY":token}, params=params).json()

def getTrades(token, secretKey, symbol, timestamp=getTimestamp(), limit=None, fromId=None, recvWindow=None):
	#gets account trades
	global baseURL, accountTradesURL
	message="symbol={0}&timestamp={1}".format(symbol, timestamp)
	params={
		"symbol":symbol,
		"timestamp":timestamp,
	}
	if recvWindow:
		params['recvWindow']=recvWindow
		message+="&recvWindow={}".format(recvWindow)
	if limit:
		params['limit']=limit
		message+="&limit={}".format(limit)
	if fromId:
		params['fromId']=fromId
		message+="&fromId={}".format(fromId)
	signature = getSignature(message.encode('utf-8'), secretKey)
	params['signature']=signature
	return requests.get(baseURL+accountTradesURL, headers={"X-MBX-APIKEY":token}, params=params).json()

def buyAdvised(token, symbol, threshhold, startingPrice=None, pollingInterval=None):
	#returns true when price moves down a certain percent
	if pollingInterval==None:
		interval = 1
	if startingPrice==None:
		startingPrice = float(getPrice(token, symbol)['price'])
	while True:
		currentPrice = float(getPrice(token,symbol)['price'])
		currentDifference = (1-(currentPrice/startingPrice))*100
		if currentDifference>=threshhold:
			print("buy advised\nstartingPrice: {0}\ncurrentPrice: {1}".format(startingPrice, currentPrice))
			return True
		print("Not Yet:\nstartingPrice: {0}\ncurrentPrice: {1}".format(startingPrice, currentPrice))
		time.sleep(interval)

def sellAdvised(token, symbol, threshhold, startingPrice=None, pollingInterval=None):
	#returns true when price up a certain percent
	if pollingInterval==None:
		interval = 1
	if startingPrice==None:
		startingPrice = float(getPrice(token, symbol)['price'])
	while True:
		currentPrice = float(getPrice(token,symbol)['price'])
		currentDifference = ((currentPrice-startingPrice)/startingPrice)*100
		if currentDifference>=threshhold:
			print("sell advised\nstartingPrice: {0}\ncurrentPrice: {1}".format(startingPrice, currentPrice))
			return True
		print("Not Yet:\nstartingPrice: {0}\ncurrentPrice: {1}".format(startingPrice, currentPrice))
		time.sleep(interval)




buyAdvised(token, "XRPETH", 1)





#print(newOrder(token, secretKey, "ETHBTC", "BUY", "LIMIT", "1", price=.9, timeInForce="GTC", live=False))





