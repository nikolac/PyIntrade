import urllib, time, uuid
from lxml import etree
import pprint

def _getXmlStr(x):
        try:
                return etree.tostring(x, pretty_print=True)
        except:
                return "Parse Fail: %s" %(x)

def pXml(x):
    print _getXmlStr(x)

def _getMessageType(cd):
    msgTypes = {
            "T":"Execution (Trade)"
            ,"D":"Canceled by exchange"
            ,"E":"Contract Expiry"
            ,"J":"Rejected Cancel Request"
            ,"M":"Message"
            ,"R":"Rejected Order"
            ,"S":"Contract scratched"
            ,"V":"Stop Activated"
            ,"X":"Order Expired (for GTS or GTT)"
    }

    if msgTypes.has_key(cd):
        return msgTypes[cd]
    else:
        return "Unknown message code [%s]" % (cd)

class IntradeError(Exception):
        pass

class IntradeResponseError(IntradeError):
        def __init__(self, resp):
                self.resp = _getXmlStr(resp)
                try:
                        self.requestOp = resp.attrib['requestOp']
                        self.timestamp = long(resp.attrib['timestamp'])
                        self.errorcode = resp.xpath('errorcode')[0].text
                        self.faildesc = resp.xpath('faildesc')[0].text
                        self.type = "Known"
                except:
                        self.type = "Unknown"
        def __str__(self):
                if self.type == "Known":
                        return "[%s]: %s" % (
                                self.errorcode, self.faildesc)
                else:
                        return "Unknown\n\n%s" % ( _getXmlStr(resp) )

                             
class Position:
        def __init__(self, position):
                self.conId = int(position.attrib['conID'])
                self.quantity =int( position.xpath('quantity')[0].text)
                self.totalCost =float( position.xpath('totalCost')[0].text)
                self.trueTotalCost = float(position.xpath('trueTotalCost')[0].text)
                self.totalIM = float(position.xpath('totalIM')[0].text)
                self.openIM = float(position.xpath('openIM')[0].text)
                self.bidAmt = float(position.xpath('bidAmt')[0].text)
                self.bidQty = int(position.xpath('bidQty')[0].text)
                self.offerAmt = float(position.xpath('offerAmt')[0].text)
                self.offerQty = int(position.xpath('offerQty')[0].text)
                self.netPL = float(position.xpath('netPL')[0].text)
             
class Balance:
        def __init__(self, resp):
                self.timestamp = long(resp.attrib['timestamp'])
                self.ccy = resp.xpath('ccy')[0].text
                self.available = float(resp.xpath('available')[0].text)
                self.frozen = float(resp.xpath('frozen')[0].text)
  
class Order:
        def __init__(self, conId = -1, side = "", limitPrice = -1, quantity = -1,
                     orderType = "L", timeInForce = "GTC", touchPrice = ""):
                self.conId = conId
                self.side = side
                self.limitPrice = limitPrice
                self.quantity = quantity
                self.orderType = orderType
                self.timeInForce = timeInForce
                self.touchPrice = touchPrice
                self.userReference = self.generateUserReference()

        def toMap(self):
                val =  'conID=%s,side=%s,limitPrice=%s,quantity=%s' %(
                        self.conId, self.side, self.limitPrice, self.quantity)

                if self.orderType != "":
                        val = val + ",orderType=%s" % (self.orderType)
                        
                val = val + ",timeInForce=%s" %(self.timeInForce)

                if self.orderType == 'T':
                        val = val + ",touchPrice=%s" % (self.touchPrice)

                if self.userReference != "":
                        val = val + ",userReference=%s" % (self.userReference)
                  
                return { "order": val }
        
        def generateUserReference(self):
                return str(uuid.uuid4())[:20]
        
class OrderResponse:
        def __init__(self, resp):
                self.orderId = -1
                self.side = resp.xpath('side')[0].text
                self.quantity = int(resp.xpath('quantity')[0].text)
                self.limitprice = float(resp.xpath('limitprice')[0].text)
                self.success = bool(resp.xpath('success')[0].text)
                self.timeInForce = resp.xpath('timeInForce')[0].text
                self.timeToExpire = long(resp.xpath('timeToExpire')[0].text)
                self.failreason = ""
                fr = resp.xpath('failreason')
                
                if len(fr) == 1:
                        self.failreason = fr[0].text
                else:
                        self.orderId = int(resp.attrib['orderID'])           
                
class OpenOrder:
        def __init__(self, resp):
                self.orderId = int(resp.attrib['orderID'])
                self.conId = int(resp.xpath('conID')[0].text)
                self.quantity = int(resp.xpath('quantity')[0].text)
                self.limitPrice = float(resp.xpath('limitprice')[0].text)
                self.orderType = resp.xpath('type')[0].text
                self.side = resp.xpath('side')[0].text
                self.originalQuantity = int(resp.xpath('originalQuantity')[0].text)
                self.userReference = resp.xpath('userReference')[0].text
                self.timeInForce = resp.xpath('timeInForce')[0].text
                self.touchPrice = float(resp.xpath('touchprice/text()')[0])
                vt =  resp.xpath('visibleTime/text()')
                if len(vt):
                    self.visibleTime = vt[0]
                else:
                    self.visibleTime = -1
                

class UserOrder:
        def __init__(self, resp):
                self.orderId = resp.attrib['orderID']
                self.conId = int(resp.xpath('conID')[0].text)
                self.quantity = int(resp.xpath('quantity')[0].text)
                self.limitPrice = float(resp.xpath('limitprice')[0].text)
                self.side = resp.xpath('side')[0].text
                self.originalQuantity = int(resp.xpath('orig_quantity')[0].text)
                self.userReference = resp.xpath('userReference')[0].text
                self.timeInForce = int(resp.xpath('timeInForce')[0].text)
                self.numFills = int(resp.xpath('numFills')[0].text)
                self.status = resp.xpath('status')[0].text
                
class MultiOrder:
        def __init__(self, sessionData, orders, cancelPrevious = "false"):
                self.sessionData = sessionData
                self.ordersByUserRef = {}
                self.orders = []
                self.cancelPrevious = cancelPrevious
                for order in orders:
                        self.orders.append(order)
                        
        def toMap(self):
                m = []
                m.append( { "sessionData" : self.sessionData } )
                m.append( { "cancelPrevious" : self.cancelPrevious } )

                for order in self.orders:
                        m.append( order.toMap() )
                return m

class Message:
        def __init__(self, resp):
                self.msgId = int(resp.attrib['msgID'])
                self.conId = int(resp.xpath('conID')[0].text)
                self.symbol = resp.xpath('symbol')[0].text
                self.readFlag = bool(resp.xpath('readFlag')[0].text)
                self.typeCd = resp.xpath('type')[0].text
                self.typeDesc = _getMessageType(self.typeCd)
                self.msg = resp.xpath('msg')[0].text
                self.price = float(resp.xpath('price')[0].text)
                self.quantity = int(resp.xpath('quantity')[0].text)
                self.side = resp.xpath('side')[0].text
                self.timestamp = long(resp.xpath('timestamp')[0].text)

        def __str__(self):
            return "msgid=%s,conId=%s,symbol=%s,readFlag=%s,typeCd=%s,typeDesc=%s,msg=%s" % (
                    self.msgId
                    ,self.conId
                    ,self.symbol
                    ,self.readFlag
                    ,self.typeCd
                    ,self.typeDesc
                    ,self.msg
                ) + ",price=%s,quantity=%s,side=%s,timestamp=%s" % (
                    self.price
                    ,self.quantity
                    ,self.side
                    ,self.timestamp
                )


class Trade:
        def __init__(self, resp):
                self.conId = int(resp.xpath('conID')[0].text)
                self.orderId= int(resp.xpath('orderID')[0].text)
                self.side= resp.xpath('side')[0].text
                self.quantity= int(resp.xpath('quantity')[0].text)
                self.price= float(resp.xpath('price')[0].text)
                self.executionTime= long(resp.xpath('executionTime/text()')[0])

        def __str__(self):
                return "conId=%s,orderId=%s,side=%s,quantity=%s,price=%s,executionTime=%s" % (
                        self.conId
                        ,self.orderId
                        ,self.side
                        ,self.quantity
                        ,self.price
                        ,self.executionTime
                )

class Contract:
        def __init__(self, resp):
                self.resp = resp
                self.ccy= resp.attrib['ccy']
                self.id = int(resp.attrib['id'])
                self.inRunning = resp.attrib['inRunning']
                self.state = resp.attrib['state']
                self.tickSize = float(resp.attrib['tickSize'])
                self.tickValue = float(resp.attrib['tickValue'])
                self.type = resp.attrib['type']
                self.name = resp.xpath('name')[0].text
                self.symbol = resp.xpath('symbol')[0].text
                self.totalVolume = int(resp.xpath('totalVolume')[0].text)

        def __str__(self):
            return _getXmlStr(self.resp)
class Event:
        def __init__(self, resp):
                self.endDate = resp.attrib['EndDate']
                self.startDate = resp.attrib['StartDate']
                self.groupId = int(resp.attrib['groupID'])
                self.id = int(resp.attrib['id'])
                self.description = resp.xpath('Description')[0].text
                self.name = resp.xpath('name')[0].text
                self.contracts = []
                cs = resp.xpath('contract')
                for c in cs:
                        self.contracts.append( Contract(c) )

class EventGroup:
        def __init__(self,resp):
                self.id = int(resp.attrib['id'])
                self.name = resp.xpath('name')[0].text
                self.events = []
                es = resp.xpath('Event')
                for e in es:
                       self.events.append( Event(e) )

class EventClass:
        def __init__(self,resp):
                self.id = int(resp.attrib['id'])
                self.name = resp.xpath('name')[0].text
                self.eventGroups = []
                egs = resp.xpath('EventGroup')
                for eg in egs:
                        self.eventGroups.append( EventGroup(eg) )

class MarketData:
        def __init__(self,resp):
                self.timestamp = long(resp.attrib['intrade.timestamp'])
                self.eventClasses = []
                ecs = resp.xpath('EventClass')
                for ec in ecs:
                        self.eventClasses.append( EventClass(ec) )

class Offer:
        def __init__(self, resp):
                self.price = float(resp.attrib['price'])
                self.quantity = int(resp.attrib['quantity'])

class Bid:
        def __init__(self, resp):
                self.price = float(resp.attrib['price'])
                self.quantity = int(resp.attrib['quantity'])

class OrderBook:
        def __init__(self, resp):
                self.bids = []
                self.offers = []

                bs = resp.xpath('bids/bid')
                for b in bs:
                        self.bids.append( Bid(b) )
                        
                ofs = resp.xpath('offers/offer')
                for of in ofs:
                        self.offers.append ( Offer(of) )

        def getLatestBidPrice(self):
            if len(bids) > 0:
                return bids[0].price
            else:
                return -1

        def getLatestAskPrice(self):
            if len(offers) > 0:
                return offers[0].price
            else:
                return -1 
                        
class PriceContractInfo:
        def __init__(self, resp):
                self.resp = resp
                if resp.attrib.has_key('close'):
                    self.close = float(resp.attrib['close'])
                else:
                    self.close = -1


                self.conId = int(resp.attrib['conID'])

                if resp.attrib.has_key('lstTrdPrc'):
                    self.lastTradePrice = float(resp.attrib['lstTrdPrc'])
                else:
                    self.lastTradePrice = -1

                if resp.attrib.has_key('lstTrdTme') and resp.attrib['lstTrdTme'] != '-':
                    self.lastTradeTime = long(resp.attrib['lstTrdTme'])
                else:
                    self.lastTradeTime = -1

                self.state = resp.attrib['state']
                self.volume = int(resp.attrib['vol'])

                if len(resp.xpath('symbol')) > 0:
                    self.symbol = resp.xpath('symbol')[0].text
                else:
                    self.symbol = ""

                o = resp.xpath('orderBook')
                if len(o) > 0:
                    self.orderBook = OrderBook( o[0] )
                else:
                    self.orderBook = None

        def __str__(self):
            return _getXmlStr(self.resp)

class ContractBookInfo:
        def __init__(self, resp):
                self.resp = resp
                self.lastUpdatedTime = long(resp.attrib['lastUpdateTime'])
                self.priceContractInfos = []

                pis = resp.xpath('contractInfo')
                for pi in pis:
                        self.priceContractInfos.append( PriceContractInfo(pi) )
        def __str__(self):
            return _getXmlStr(self.resp)

class ContractInfo:
        def __init__(self, resp):
                self.resp = resp
                self.ccy = resp.attrib['ccy']
                self.conId = int(resp.attrib['conID'])
                if resp.attrib.has_key('close'):
                    self.close = float(resp.attrib['close'])
                else:
                    self.close = -1

                
                if resp.attrib.has_key('dayhi') and resp.attrib['dayhi'] != '-':
                    self.dayhi = float(resp.attrib['dayhi'])
                else:
                    self.dayhi = -1

                if resp.attrib.has_key('daylo') and resp.attrib['daylo'] != '-':
                    self.daylo = float(resp.attrib['daylo'])
                else:
                    self.daylo = -1

                if resp.attrib.has_key('dayvol'):    
                    self.dayvol = int(resp.attrib['dayvol'])
                else:
                    self.dayvol = -1

                self.lifehi = float(resp.attrib['lifehi'])
                self.lifelo = float(resp.attrib['lifelo'])
                
                if resp.attrib.has_key('lstTrdPrc') and resp.attrib['lstTrdPrc'] != '-':
                    self.lstTrdPrc = float(resp.attrib['lstTrdPrc'])
                else:
                    self.lstTrdPrc = -1

                if resp.attrib.has_key('lstTrdTme')  and resp.attrib['lstTrdTme'] != '-':   
                    self.lstTrdTme = long(resp.attrib['lstTrdTme'])
                else:
                    self.lstTrdTme = -1

                self.maxMarginPrice = float(resp.attrib['maxMarginPrice'])
                self.minMarginPrice = float(resp.attrib['minMarginPrice'])
                self.state = resp.attrib['state']
                self.tickSize = float(resp.attrib['tickSize'])
                self.tickValue = float(resp.attrib['tickValue'])
                tv = resp.attrib['totalvol']
                if tv[-1:] == 'k':
                    self.totalVolume = float(tv[:-1]) *1000
                else:
                    self.totalVolume = float(tv)

                self.type = resp.attrib['type']

                if resp.attrib.has_key('marginLinked'):
                    self.marginLinked = resp.attrib['marginLinked']
                else:
                    self.marginLinked = ''
                

                if resp.attrib.has_key('marginGroupId'):
                        self.marginGroupId = resp.attrib['marginGroupId']
                else:
                    self.marginGroupId = -1
                self.symbol = resp.xpath('symbol')[0].text

                if resp.attrib.has_key('expiryTime'):
                    self.expiryTime = long(resp.attrib['expiryTime'])
                else:
                    self.expiryTime = -1

                if resp.attrib.has_key('expiryPrice'):
                    self.expiryPrice = float(resp.attrib['expiryPrice'])
                else:
                    self.expiryPrice = -1
                
        def __str__(self):
                return _getXmlStr(self.resp)
        
                
class ClosingPrice:
        def __init__(self, resp):
                self.date = resp.attrib['date']
                self.dt = long(resp.attrib['dt'])
                self.price = float(resp.attrib['price'])
                self.sessionHi = float(resp.attrib['sessionHi'])
                self.sessionLo = float(resp.attrib['sessionLo'])

class TimeSale:
        def __init__(self, resp):
                ps = resp.split(',')
                self.timestamp = long(ps[0])
                self.date = ps[1].strip()
                self.price = float(ps[2])
                self.quantity = int(ps[3])

        def __str__(self):
            return "timestamp=%s,date=%s,price=%s,quantity=%s" % (
                    self.timestamp
                    ,self.date
                    ,self.price
                    ,self.quantity
                )
                
class CancelResponse:
        def __init__(self, resp):
                self.isEndOfDay = bool(resp.xpath('isEndOfDay')[0].text)
                self.didCancel = bool(resp.xpath('didCancel')[0].text)
                self.orderCancelList = []

                oids = resp.xpath('orderCancelList/ordID/text()')
                for oid in oids:
                    self.orderCancelList.append(oid)

                
class Intrade:
        def __init__(self, membershipNum, password, live = False):
                if live:
                        self.BASE_URL = 'https://api.intrade.com'
                else:
                        self.BASE_URL = 'http://testexternal.intrade.com'
                        
                self.ALL_CONTRACTS_URL = self.BASE_URL +\
                                        '/jsp/XML/MarketData/xml.jsp?'
                self.CONTRACTS_BY_EVENT_CLASS_URL = self.BASE_URL + \
                                        '/jsp/XML/MarketData/XMLForClass.jsp?'
                self.CURRENT_PRICE_URL = self.BASE_URL + \
                                         '/jsp/XML/MarketData/ContractBookXML.jsp?'
                self.CONTRACT_INFO_URL = self.BASE_URL +\
                                         '/jsp/XML/MarketData/ConInfo.jsp?'
                self.HISTORICAL_CLOSING_PRICE_URL = self.BASE_URL + \
                                        '/jsp/XML/MarketData/ClosingPrice.jsp?'
                self.TIME_SALES_INFO_URL = self.BASE_URL + \
                                           '/jsp/XML/TradeData/TimeAndSales.jsp?'
                self.TRADE_URL = self.BASE_URL + \
                                         '/xml/handler.jsp'
                
                self.sessionData = ""
                self.username = ""
                self.lastLogin = ""
                self.loggedIn = False

                self.membershipNumber = membershipNum
                self.password = password

                self.getLogin()

        def toXml(self, l):
                xml = ""
                if type(l) == list:
                        for i in l:
                                xml = xml + self.toXml(i)
                if type(l) == dict:
                        for i in l:
                                xml = xml + "<%s>%s</%s>" % (
                                        i, self.toXml(l[i]), i)
                if type(l) == str or type(l) == int or type(l) == float or type(l) == long:
                        xml = xml + str(l)
                return xml

        def buildDataRequest(self, url, params):
                parts = []
                for p in params:
                        if type(params[p]) == str:
                                parts.append( p + '=' + params[p] )
                        if type(params[p]) == list:
                                for i in params[p]:
                                        parts.append( p + '=' + str(i) )
                return url + "&".join(parts)
                        
                
        def buildRequest(self, op, params):
                return "<xmlrequest requestOp='%s'>%s</xmlrequest>" % (
                        op, self.toXml(params))

        def sendDataRequest(self, req):
                respXml = urllib.urlopen(url = req).read()
                return etree.fromstring(respXml)

        def sendTextRequest(self, req):
                return urllib.urlopen(url = req).read()
        
        def sendRequest(self, url, req, attempt = 0):
                respXml = urllib.urlopen(url=url, data = req).read()
                f = etree.fromstring(respXml)
                resp = f.xpath('/tsResponse')[0]

                if resp.attrib['resultCode'] == '-1':
                        if resp.xpath('errorcode')[0].text == '105' and attempt == 0:
                                return self.sendRequest(url, req, attempt = 1)
                        else:
                                raise IntradeResponseError(resp)
                
                return resp

        def getLogin(self):
                op = 'getLogin'
                params =  {
                        "membershipNumber": self.membershipNumber,
                        "password"        : self.password
                }
                
                req = self.buildRequest(op, params)
                resp =  self.sendRequest(self.TRADE_URL, req)
                
                self.sessionData = resp.xpath('sessionData')[0].text
                self.loggedIn = True
                self.username = resp.xpath('username')[0].text
                self.lastLogin = long(resp.attrib['timestamp'])
                
        def getBalance(self):
                op = 'getBalance'
                params = {
                        "sessionData" : self.sessionData
                }

                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)

                return Balance(resp)
                      
        def multiOrderRequest(self, orders, cancelPrevious = False):
                op = "multiOrderRequest"
                m = MultiOrder(self.sessionData, orders, cancelPrevious)
                params = m.toMap()

                req = self.buildRequest(op,params)
                resp = self.sendRequest(self.TRADE_URL, req)

                orderResponses = []
                os = resp.xpath('order')
                
                for o in os:
                        orderResponses.append( OrderResponse(o) )

                return orderResponses

        def cancelOrdersById(self, orderIds):
                op = 'cancelMultipleOrdersForUser'
                params = []
                for oid in orderIds:
                        params.append( { "orderID": oid } )
                params.append( {"sessionData": self.sessionData })
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                return CancelResponse(resp)
                
        def cancelAllOrdersInContract(self, contractId):
                op = 'getCancelAllInContract'
                params = { "contractID": contractId
                           , "sessionData": self.sessionData
                        }

                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                return CancelResponse(resp)

        def cancelAllBids(self, contractId):
                op = 'getCancelAllBids'
                params = { "contractID": contractId
                           ,"sessionData": self.sessionData
                        }
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                return CancelResponse(resp)

        def cancelAllOffers(self, contractId):
                op = 'getCancelAllOffers'
                params = { "contractID": contractId
                           , "sessionData": self.sessionData
                        }
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                return CancelResponse(resp)

        def cancelOrdersInEvent(self, eventId):
                op = 'cancelAllInEvent'
                params = { "eventID": eventId
                           ,"sessionData": self.sessionData
                           }
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                return CancelResponse(resp)

        def cancelAllOrders(self):
                op = 'cancelAllOrdersForUser'
                params = {'sessionData':self.sessionData}
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                return CancelResponse(resp)
                
        def getPositions(self, contractId = ""):
                op = 'getPosForUser'
                params = { "sessionData": self.sessionData }
                if contractId != "":
                        params["contractId"] = contractId
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                ps = []
                positions = resp.xpath('position')
                for position in positions:
                        ps.append( Position(position) )
                return ps
                                

        def getOpenOrders(self, contractId = ""):
                op = 'getOpenOrders'
                params = { "sessionData": self.sessionData }

                if contractId != "":
                        params["contractID"] = contractId

                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)
                os = []
                
                orders = resp.xpath('order')
                for order in orders:
                        os.append( OpenOrder(order)  )
                return os

        def getOrdersByOrderId(self, oids):
                op = 'getOrdersForUser'
                params = []
                
                for oid in oids:
                        params.append({"orderID":oid})
                params.append({ "sessionData": self.sessionData })
                
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)

                os = []
                
                orders = resp.xpath('order')
                for order in orders:
                        os.append( UserOrder(order))
                return os

        def getMessages(self, timestamp = ""):
                op = 'getUserMessages'
                params = {'sessionData':self.sessionData}
                if timestamp != '':
                        params['timestamp'] = timestamp

                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)

                messages = []
                
                ms = resp.xpath('msg')
                for m in ms:
                        messages.append( Message(m) )

                return messages

        def setAsRead(self, msgIds):
                op = 'setAsRead'
                params = [{ "sessionData": self.sessionData },]

                for msgId in msgIds:
                        params.append( {"userNotificationID": msgId} )

                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)

        def getTrades(self, timestamp = 1111111111111,
                             endDate = "", contractId = ""):
                op = 'getTradesForUser'
                params = {"sessionData":self.sessionData}
                if timestamp != "":
                        params["tradeStartTimestamp"] = timestamp
                if endDate != "":
                        params["endDate"] = endDate
                if contractId !="":
                        params["contractID"] = contractId

                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)

                trades = []
                ts = resp.xpath('trade')
                for t in ts:
                        trades.append(Trade(t))
                
                return trades       

        def checkMessages(self):
                op = 'getGSXToday'
                params = {
                        "sessionData": self.sessionData,
                        "checkMessages": "true"
                        }
                req = self.buildRequest(op, params)
                resp = self.sendRequest(self.TRADE_URL, req)

                hasMessages = 0
                if resp.attrib.has_key('hasMessages'):
                        hasMessages = int(resp.attrib['hasMessages'])

                return hasMessages

        def getMarketData(self):
                req = self.buildDataRequest( self.ALL_CONTRACTS_URL, {})
                resp = self.sendDataRequest(req)
                
                return MarketData(resp)
        
        def getMarketDataByEventClass(self,eventClass):
                req = self.buildDataRequest( self.CONTRACTS_BY_EVENT_CLASS_URL,
                                             {"classID":eventClass})
                resp = self.sendDataRequest(req)
                return EventClass(resp)

        def getPriceInfo(self, conIds, timestamp='', depth = '1'):
                args = {"depth":depth, 'id' : conIds}
                if timestamp != "":
                        args["timestamp"] = timestamp 
                
                req = self.buildDataRequest( self.CURRENT_PRICE_URL,
                                             args)
                resp = self.sendDataRequest(req)
                return ContractBookInfo(resp)

        def getContractInfo(self, conIds):
                req = self.buildDataRequest( self.CONTRACT_INFO_URL,
                                             {'id':conIds})
                resp = self.sendDataRequest(req)
                conInfos = []
                cons = resp.xpath('/conInfo/contract')
                for con in cons:
                        conInfos.append( ContractInfo(con) )
                return conInfos

        def getClosingPrice(self, conId):
                req = self.buildDataRequest( self.HISTORICAL_CLOSING_PRICE_URL,
                                             {"conID":conId})
                resp = self.sendDataRequest(req)
                closingPrices = []

                cps = resp.xpath('ClosingPrice/cp')
                for cp in cps:
                    closingPrices.append (ClosingPrice(cp))
                return closingPrices

        def getDailyTimeAndSales(self, conId):
                req = self.buildDataRequest( self.TIME_SALES_INFO_URL,
                                             {"conID":conId})
                resp = self.sendTextRequest(req)
                ts = resp.split('\n')
                tSales = []

                for t in ts:
                    if t != "":
                        tSales.append (TimeSale(t))
                return tSales

        def getIntradeTime(self):
            op = 'getGSXToday'
            params = {
                    "sessionData": self.sessionData,
                    "checkMessages": "true"
                    }
            req = self.buildRequest(op, params)
            resp = self.sendRequest(self.TRADE_URL, req)

            return long(resp.attrib['timestamp'])
