from Intrade import *
import time
import datetime

class IntradeSessionError(Exception):
	def __init__(self, cd, msg):
		self.cd = cd
		self.msg = msg

	def __str__(self):
		return "[%s] %s" %(self.cd, self.msg)

class IntradeSession:
	def __init__(self, memNum, pw):
		self.n = Intrade(memNum,pw)
		self.md = None
		self.event = None
		self.contract = None
		self.contractInfo = None
		self.priceInfo = None
		self.timeAndSales = None
		self.positions = []
		self.timeDelay = 0

	def getEventName(self):
		return self.event.name
		

	def getEventClass(self, classId):
		return self.n.getMarketDataByEventClass(classId)

	def refreshMarketData(self):
		self.md = self.n.getMarketData()

	def refreshContractInfo(self):
		self.contractInfo = self.n.getContractInfo([self.contract.id,])[0]
		
	
	def isExpired(self):
		return self.contractInfo.state == 'S'
		

	def getExpirationTime(self):
		return self.contractInfo.expiryTime
		

	def getExpirationPrice(self):
		return self.contractInfo.expiryPrice
		

	def isClosed(self):
		self.refreshContractInfo()
		return self.isExpired()
		

	def isOpen(self):
		return not self.isClosed()

	def refreshPositions(self):
		if self.isOpen():
			self.positions = self.n.getPositions(self.contract.id)
			return True
		else:
			return False

	def placeOrder(self, price, quantity):
		if self.isOpen():
			return False
		else:
			return False

	def refreshTimeAndSales(self):
		if self.isOpen():
			self.timeAndSales = self.n.getDailyTimeAndSales(self.contract.id)

	def refreshPriceInfo(self):
		if self.isOpen():
			self.priceInfo = self.n.getPriceInfo([self.contract.id,]).priceContractInfos[0]



	def getTime(self):
		self.timeDelay =  d.n.getIntradeTime() - long(time.time()*1000)
		return self.n.getIntradeTime()

	def getAdjustedTime(self):
		return long(time.time()*1000) + self.timeDelay

	def startTrading(self):
		while self.shouldContinue():
			if self.havePositions():
				self.sell()
			else:
				self.buy()

		return "Market Closed!"

	

	def buy(self):
		targetPrice = self.getBuyPrice()
		latestPrice = self.getLatestAsk()

		while latestPrice > targetPrice and self.isOpen():
			targetPrice = self.getBuyPrice()
			latestPrice = self.getLatestAsk()

		if self.isOpen():
			targetQuantity = self.getBuyQuantity(latestPrice)
			success = self.placeOrder(latestPrice,targetQuantity)

			return success
		else:
			return False


	def shouldContinue(self):
		return self.isOpen()

	def sell(self):
		return

	def getBuyPrice(self):
		return

	def getBuyQuantity(self, latestPrice):
		return

	def getSellPrice(self):
		return

	def getLatestPrice(self):
		self.refreshContractInfo()
		return self.contractInfo.lstTrdPrc

	def getLatestBid(self):
		self.refreshPriceInfo()
		return self.priceInfo.orderBook.bids[0].price

	def getLatestAsk(self):
		self.refreshPriceInfo()
		return self.priceInfo.orderBook.offers[0].price

class DowDailyEvent(IntradeSession):
	def __init__(self, memNum, pw):
		IntradeSession.__init__(self, memNum, pw)
		self.event = self.getDowEvent()


	def getDowEvent(self):
		ec = self.getEventClass('67')
		todayDowName = self.getTodayEventName()

		
		for eg in ec.eventGroups:
			for e in eg.events:
				if todayDowName in e.name:
					return e

		raise IntradeSessionError('0',"Event (%s) does not exist" % (todayDowName))

	def getTodayEventName(self):
		d = datetime.datetime.now()
		return "Daily DJIA Close. " + d.strftime('%a %b %d 20%y')

class DowDailyCloseHigherSession(DowDailyEvent):
	def __init__(self, memNum, pw):
		DowDailyEvent.__init__(self,memNum, pw)

		for c in self.event.contracts:
			if 'HIGHER' in c.name:
				self.contract = c
				self.refreshContractInfo()

		if not self.contract:
			raise IntradeSessionError('1',"Contract does not exist")



class DowMonthlyEvent(IntradeSession):
	def __init__(self,memNum,pw):
		IntradeSession.__init__(self, memNum, pw)
		self.event = self.getDowEvent()

	def getDowEvent(self):
		ec = self.getEventClass('67')
		monthDowName = self.getMonthEventName()

		
		for eg in ec.eventGroups:
			for e in eg.events:
				if monthDowName in e.name:
					return e
		raise IntradeSessionError('0',"Event (%s) does not exist" % (monthDowName))

	def getMonthEventName(self):
		d = datetime.datetime.now()
		return d.strftime('%B %Y') + " DJIA Close"


class DowMonthlyCloseHigherSession(DowMonthlyEvent):
	def __init__(self, memNum, pw):
		DowMonthlyEvent.__init__(self,memNum, pw)

		for c in self.event.contracts:
			if 'ABOVE 13000' in c.name:
				self.contract = c
				self.refreshContractInfo()
				self.refreshPriceInfo()

		if not self.contract:
			raise IntradeSessionError('1',"Contract does not exist")



if __name__=="__main__":
	 

	 d= DowMonthlyCloseHigherSession('10014', 'intrade1')
	 print d.contractInfo
	 print d.getEventName()
	 print d.isExpired()
	 print d.getExpirationTime()
	 print d.getExpirationPrice()
	 print d.isClosed()
	 print d.getTime() - long(time.time()*1000)
	 print d.getTime() - d.getAdjustedTime()  
	 print 'Bid:',d.getLatestBid()
	 print 'Offer:',d.getLatestAsk()
	 print 'Latest Price:',d.getLatestPrice()
	 