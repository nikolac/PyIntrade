from numpy import *
import ols, time, datetime
import matplotlib.pyplot as plt

class FinancialDataSet:
	def __init__(self, data):
		#print 'Initializing Financial Data...'
		self.__data = array(data)
		self.__times = self.__data[:, 0]
		self.__prices = self.__data[:, 1]
		self.__volume = self.__data[:, 2]
		self.__ema = {}
		self.__pricesByPeriod = []
		self.__periodInSeconds = 60
		self.__periodValueType = 'C'

		for d in data:
			self.__addPeriodData(d)

		#print 'Finished initializing'

	def size(self):
		return len(self.__data)

	def periodSize(self):
		return len(self.__pricesByPeriod)

	def lastPeriodIndex(self):
		return self.periodSize() - 1

	def lastPeriodPrice(self):
		return self.__pricesByPeriod[-1:]

	def priceAtPeriod(self, i):
		return self.__pricesByPeriod[i]

	def __appendPricePeriod(self, val):
		self.__pricesByPeriod.append(val)

	def __setPeriodAt(self, ordT, val):
		prevP = self.lastPeriodPrice()
		prevT = self.lastPeriodIndex()

		while ordT > prevT:
			self.__appendPricePeriod( prevP )
			prevT = self.lastPeriodIndex()


		self.__appendPricePeriod( val )
		if self.__ema.has_key(ordT):
			self.__ema.pop(ordT,None)

	def addDataBatch(self, data):
		data = array(data)
		append(self.__data, data)
		append(self.__times, data[:,0])
		append(self.__prices, data[:,1])
		append(self.__volume, data[:,2])
		for d in data:
			self.__addPeriodData(d)

	def addData(self, data):
		append(self.__data, data)
		append(self.__times, data[0])
		append(self.__prices, data[1])
		append(self.__volume, data[2])
		self.__addPeriodData(data)

	def __addPeriodData(self, data):
		ordT = self.__timeToOrd(data[0])
		p = data[1]
		self.__setPeriodAt(ordT, p)

	def getDataAt(self,n):
		return self.__data[n]

	def getData(self):
		return self.__data

	def getTimes(self): 
		return self.__times

	def getPrices(self):
		return self.__prices

	def getVolume(self):
		return self.__volume

	def getlastTime(self):
		return self.__times[:-1]

	def getFirstTime(self):
		return self.__times[0]

	def timePriceCorr(self):
		return corrcoef([self.__times, self.__prices])[0][1]

	def printData(self):
		print self.__data

	def printInfo(self):
		print "Size: %s\nTimePriceCorr: %s\nMinPrice:%s\nMaxPrice:%s" % (
			self.size()
			, self.timePriceCorr()
			, self.minPrice()
			, self.maxPrice()
			)

	def getSliceInTimeRange(self, fromTime = -1, toTime = 9999999999999):
		sData = []

		for fd in self.__data:
			if fd[0] > fromTime and fd[0] < toTime:
				sData.append(fd)
				if fd[0] >= toTime:
					break

		if len(sData):
			return FinancialDataSet(sData)
		else:
			return None

	def getSliceOrdRange(self,fromN = 0, toN = -1):
		if toN == -1:
			toN = self.size()
		
		nd = self.__data[fromN:toN]

		if len(nd):
			return FinancialDataSet( nd  )
		else:
			return None

	def getSliceLastN(self, n):
		s = self.size()
		if n > s:
			fromN = 0
		else:
			fromN = s - n
		
		return self.getSliceOrdRange(fromN)

	def sliceLastHr(self):
		return self.getSliceTimeRange(self.__lastNHrTme())


	def __lastNHrTme(self, n = 1):
		return self.__t() - self.__hrToMs(n)

	def __hrToMs(self, hrs):
		return self.__minToMs(hrs * 60) 
	
	def __minToMs(self, mins):
		return self.__secToMs(mins * 60)
	
	def __secToMs(self, secs):
		return secs*1000

	def __t(self):
		return time.time()*1000

	def minPrice(self):
		return self.__prices.min()

	def maxPrice(self):
		return self.__prices.max()

	def minPriceData(self):
		i = self.__prices.argmin()
		return self.getDataAt(i), i

	def maxPriceData(self):
		i = self.__prices.argmax()
		return self.getDataAt(i), i

	def printOlsSummary(self):
		m = ols.ols(self.getPrices(), self.getTimes(), "Price", ["Time"])
		m.summary()

	def plot(self):
		plt.plot(self.getTimes(), self.getPrices())
		plt.show()

	def emaAtTime(self, t):
		return self.__getEma(self.__timeToOrd(t), self.periodSize())

	def __getEma(self, ordT, n):
		if ordT <= 0:
			return self.pricePeriodAt(0)

		if not self.__ema.has_key(ordT):
			prevEma = self.__getEma(ordT - 1, n)
			p = self.pricePeriodAt(ordT)
			k = 2/(n + 1)
			tEma = (p * k )+ (prevEma * 1-k)
			self.__ema[ordT] = tEma
			return tEma
		else:
			return self.__ema[ordT]
		


	def __timeToOrd(self, t):
		start = self.getFirstTime()
		diffT = t - start 
		return diffT / self.__secToMs(self.__periodInSeconds)

		



