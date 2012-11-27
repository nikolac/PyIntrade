from Intrade import *
from FinancialData import *
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
		self.financialData = None
		self.md = None
		self.event = None
		self.contract = None
		self.contractInfo = None
		self.priceInfo = None
		self.timeAndSales = []
		self.timeDelay = 0
		self.historicalAsks = []
		self.historicalBids = []

		self.sessionProfit = 0
		self.moneyInvested = 0

		self.MAX_PERCENT_INVEST = 10
		

	def getEventName(self):
		return self.event.name
		
	def getEventClass(self, classId):
		return self.n.getMarketDataByEventClass(classId)

	def refreshMarketData(self):
		self.md = self.n.getMarketData()

	def refreshContractInfo(self):
		self.contractInfo = self.n.getContractInfo([self.contract.id,])[0]
		
	def isExpired(self):
		self.refreshContractInfo()
		return self.contractInfo.isExpired()
		
	def getExpirationTime(self):
		return self.contractInfo.expiryTime
		

	def getExpirationPrice(self):
		return self.contractInfo.expiryPrice

	def isClosed(self):
		self.refreshContractInfo()
		return self.contractInfo.isClosed()

	def isOpen(self):
		return not self.isClosed()

	def havePosition(self):
		return self.getPosition() != None

	def getPosition(self):
		pos = self.n.getPositions(self.contract.id)
		if len(pos) > 0:
			self.position =  pos[0]
			return self.position
			

	def placeOrder(self, price, quantity):
		if self.isOpen():
			return False
		else:
			return False

	def refreshTimeAndSales(self):
		
		self.timeAndSales = self.n.getDailyTimeAndSales(self.contract.id)
		self.financialData = FinancialDataSet([ t.toTup() for t in self.timeAndSales])

	def getTimeAndSales(self):
		self.refreshTimeAndSales()
		return self.timeAndSales

	def refreshPriceInfo(self):
		self.priceInfo = self.n.getPriceInfo([self.contract.id,]).priceContractInfos[0]


	def getTime(self):
		self.timeDelay =  d.n.getIntradeTime() - long(time.time()*1000)
		return self.n.getIntradeTime()

	def getAdjustedTime(self):
		return long(time.time()*1000) + self.timeDelay

	def startTrading(self):
		while self.shouldContinue():
			if self.havePosition():
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
		bidPrice =  self.priceInfo.orderBook.getLatestBidPrice()
		if bidPrice > 0:
			self.historicalBids.append( (time.time(), bidPrice))
		return bidPrice

	def getLatestAsk(self):
		self.refreshPriceInfo()
		askPrice =  self.priceInfo.orderBook.getLatestOfferPrice()

		if askPrice > 0:
			self.historicalAsks.append((time.time(), askPrice))

		return askPrice

	def getAvailableCash(self):
		return self.getBalance().available

	def getInvested(self):
		return self.getBalance().frozen

	def getBalance(self):
		return self.n.getBalance()


	def getStopLossPrice(self):
		return -1

	def getPositionAvgCost(self):
		self.position = self.getPosition()
		if self.position:
			return self.position.averageCost()
		else:
			return -1

	def getTargetPrice(self):
		self.position = self.getPosition()
		if self.position:
			tenPercent = self.getPositionAvgCost() * 1.1
			return tenPercent
		else:
			-1




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
				self.refreshTimeAndSales()

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
				self.refreshTimeAndSales()

		if not self.contract:
			raise IntradeSessionError('1',"Contract does not exist")



if __name__=="__main__":

	d = DowDailyCloseHigherSession('10014', 'intrade1')
	print "Event:",d.getEventName()
	print "Contract Closed:",d.isClosed()

	d.financialData.printInfo()
	
	

	
	
	
	


	 
	 

	
	 