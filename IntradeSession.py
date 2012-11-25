from Intrade import *
import time
import datetime


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

	def getEventName(self):
		if self.event:
			return self.event.name
		else:
			return ""

	def getEventClass(self, classId):
		return self.n.getMarketDataByEventClass(classId)

	def refreshMarketData(self):
		self.md = self.n.getMarketData()

	def refreshContractInfo(self):
		if self.contract:
			self.contractInfo = self.n.getContractInfo([self.contract.id,])[0]
		
	
	def isExpired(self):
		if self.contractInfo:
			return self.contractInfo.state == 'S'
		else:
			return True

	def getExpirationTime(self):
		if self.contractInfo:
			return self.contractInfo.expiryTime
		else:
			return -1

	def getExpirationPrice(self):
		if self.contractInfo:
			return self.contractInfo.expiryPrice
		else:
			return -1

	def isClosed(self):
		self.refreshContractInfo()
		if self.contractInfo:
			return self.isExpired()
		else:
			return True

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
			self.priceInfo = self.n.getPriceInfo([self.contract.id,])


class DowDailySession(IntradeSession):
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

	def getTodayEventName(self):
		d = datetime.datetime.now()
		return "Daily DJIA Close. " + d.strftime('%a %b %d 20%y')

class DowCloseHigherSession(DowDailySession):
	def __init__(self, memNum, pw):
		DowDailySession.__init__(self,memNum, pw)

		if self.event:
			for c in self.event.contracts:
				if 'HIGHER' in c.name:
					self.contract = c
					self.refreshContractInfo()


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
		return

	def getLatestBid(self):
		self.refreshContractInfo()

	def getLatestAsk(self):
		return









if __name__=="__main__":
	 d = DowCloseHigherSession('10014', 'intrade1')

	 print d.getEventName()
	 print d.isExpired()
	 print d.getExpirationTime()
	 print d.getExpirationPrice()
	 print d.isClosed()
	 print d.startTrading()
	 print d.n.getIntradeTime()
