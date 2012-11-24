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
		self.prices = None

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
		
	def refreshPrices(self):
		if self.contract:
			self.prices = self.n.getPriceInfo([self.contract.id,])

	def isExpired(self):
		if self.contractInfo:
			return self.contractInfo.state == 'S'

	def getExpirationTime(self):
		if self.contractInfo:
			return self.contractInfo.expiryTime

	def getExpirationPrice(self):
		if self.contractInfo:
			return self.contractInfo.expiryPrice

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
		DowSession.__init__(self,memNum, pw)

		for c in self.event.contracts:
			if 'HIGHER' in c.name:
				self.contract = c
				self.refreshContractInfo()  
				self.refreshPrices()



if __name__=="__main__":
	 d = DowCloseHigherSession('10014', 'intrade1')

	 print d.getEventName()
	 print d.isExpired()
	 print d.getExpirationTime()
	 print d.getExpirationPrice()
