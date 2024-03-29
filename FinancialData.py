from numpy import *
import ols, time, datetime
import matplotlib.pyplot as plt

class FinancialDataSet:
	def __init__(self, data, periodInSeconds=60):
		#print 'Initializing Financial Data...'
		self.__data = array(data)
		self.__times = self.__data[:, 0]
		self.__prices = self.__data[:, 1]
		self.__volume = self.__data[:, 2]
		self.__ema = []
		self.__pricesByPeriod = []
		self.__periodInSeconds = periodInSeconds
		self.__periodValueType = 'C'
		

		for d in data:
			self.__addPeriodData(d)

		self.__refreshEma()
		

	def size(self):
		return len(self.__data)

	def periodSize(self):
		return len(self.__pricesByPeriod)

	def lastPeriodIndex(self):
		return self.periodSize() - 1

	def getPricesByPeriod(self):
		return self.__pricesByPeriod

	def lastPeriodPrice(self):

		return self.priceAtPeriod(self.lastPeriodIndex())

	def priceAtPeriod(self, i):
		if i >= 0 and i < self.periodSize():
			return self.__pricesByPeriod[i]
		else:
			return -1

	def __appendPricePeriod(self, val):
		self.__pricesByPeriod.append(val)

	def __setPeriodAt(self, ordT, val):
		prevP = self.lastPeriodPrice()
		prevT = self.lastPeriodIndex()

		while prevT < ordT - 1:
			self.__appendPricePeriod( prevP )
			prevT = self.lastPeriodIndex()


		if self.priceAtPeriod(ordT) == -1:
			self.__appendPricePeriod( val )
		else:
			self.__pricesByPeriod[ordT] = val

	def emaSize(self):
		return len(self.__ema)

	def addDataBatch(self, data):
		data = array(data)
		append(self.__data, data)
		append(self.__times, data[:,0])
		append(self.__prices, data[:,1])
		append(self.__volume, data[:,2])
		
		for d in data:
			self.__addPeriodData(d)

		self.__refreshEma()

	def addData(self, data):
		append(self.__data, data)
		append(self.__times, data[0])
		append(self.__prices, data[1])
		append(self.__volume, data[2])
		self.__ema = []
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
		return long(self.__times[-1][0])

	def getFirstTime(self):
		return long(self.__times[0])

	def timePriceCorr(self):
		return corrcoef([self.__times, self.__prices])[0][1]

	def printPeriodData(self):
		fTime = self.getFirstTime()
		prev = 0
		for d in self.__data:
			ordT = self.__timeToOrd(d[0])
			prevT = prev + 1

			while  prevT < ordT:
				print prevT,'    ','   ', self.priceAtPeriod(prevT)
				prevT = prevT + 1
			if ordT != prev:
				print
			print ordT,long(d[0] - fTime)/1000, d[1], self.priceAtPeriod(ordT)
			prev = ordT


	def printInfo(self):
		print "Size: %s\nTimePriceCorr: %s\nMinPrice:%s\nMaxPrice:%s \nLastPrice:%s" % (
			self.size()
			, self.timePriceCorr()
			, self.minPrice()
			, self.maxPrice()
			, self.lastPrice()
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
		return long(time.time()*1000)

	def minPrice(self):
		return self.__prices.min()

	def maxPrice(self):
		return self.__prices.max()

	def minPriceData(self):
		i = self.__prices.argmin()
		return self.getDataAt(i), i

	def lastPrice(self):
		return self.__prices[-1:][0]

	def lastData(self):
		return self.__data[-1]

	def maxPriceData(self):
		i = self.__prices.argmax()
		return self.getDataAt(i), i

	def printOlsSummary(self):
		m = ols.ols(self.getPrices(), self.getTimes(), "Price", ["Time"])
		m.summary()

	def plot(self):
		start = self.getFirstTime()
		ts = [self.__timeToFloatOrd(t) for t in self.getTimes()]
		plt.plot(ts, self.getPrices())
		a = [ordT for ordT in range(self.periodSize()) ]

		plt.plot(a, self.getPricesByPeriod())
		self.__refreshEma()
		plt.plot(a, self.__ema)
		plt.show()



	def emaAtTime(self, t):
		return self.__getEma(self.__timeToOrd(t))

	def __refreshEma(self):
		self.__ema = []
		self.__getEma(self.lastPeriodIndex())


	def __getEma(self, ordT):
		if ordT <= 0:
				p = self.priceAtPeriod(0)
				self.__ema.append(p)
				

		while self.emaSize() <= ordT:
			prevIdx = self.emaSize() - 1
			prevEma = self.__getEma(prevIdx)
			p = self.priceAtPeriod(self.emaSize())
			setSize = self.periodSize()
			ema = self.__calcEma(prevEma, setSize, p)
			self.__ema.append( ema )
		
		return self.__ema[ordT]
			

	def __calcEma(self, prevEma, setSize, curPrice):
		k = 2 / (setSize + 1.0)
		tEma = (curPrice*k) + (prevEma * (1 - k))
		return tEma

		

	def __timeToOrd(self, t):
		start =  self.getFirstTime() 
		diffT = long(t) - start 
		return  diffT / self.__secToMs(self.__periodInSeconds)
	 

	def __ordToTime(self, ordT):
		diffT = ordT * self.__secToMs(self.__periodInSeconds)
		return diffT + self.getFirstTime()

	def __timeToFloatOrd(self, t):
		start = self.getFirstTime()
		diffT = t - start
		return float(diffT)/ self.__secToMs(self.__periodInSeconds)



