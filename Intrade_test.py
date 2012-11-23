import unittest
from Intrade import *
import time


class TestIntrade(unittest.TestCase):
    def setUp(self):
        self.memNum = '10014'
        self.pw = 'intrade1'

    def test_login_empty(self):
        with self.assertRaises(IntradeResponseError):
            n = Intrade("","")
            
    def test_login_incorrect_password(self):     
        with self.assertRaises(IntradeResponseError):
           n = Intrade(self.memNum,"lkjlkj")
           
    def test_login_initial_correct(self):
        n = Intrade(self.memNum, self.pw)
        self.assertTrue(n.loggedIn)
        self.assertNotEqual(n.sessionData, "")
        self.assertNotEqual(n.lastLogin, "")
        self.assertNotEqual(n.username, "")

    def test_login_relogin_correct(self):
        n = Intrade(self.memNum, self.pw)
        n.getLogin()
        self.assertTrue(n.loggedIn, "Logged in flag")
        self.assertNotEqual(n.sessionData, "", "Session data empty")
        self.assertNotEqual(n.lastLogin, "", 'Last login')
        self.assertNotEqual(n.username, "", 'Username blank')
        

    def test_get_open_orders(self):
        n = Intrade(self.memNum, self.pw)
        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_get_open_orders_oids(self):
        n = Intrade(self.memNum, self.pw)
        
        orders = []
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
        resp = n.multiOrderRequest(orders, True)

        self.assertEqual(len(resp), 1)

        for o in resp:
            self.assertTrue(o.success)

        time.sleep(1)

        os = n.getOrdersByOrderId([resp[0].orderId,])
        self.assertEqual(len(os), 1)

        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_put_MOR_single_order(self):
        n = Intrade(self.memNum, self.pw)
        
        orders = []
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
        resp = n.multiOrderRequest(orders, True)

        self.assertEqual(len(resp), 1)

        for o in resp:
            self.assertTrue(o.success)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 1)

        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)
        
        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

        
    def test_put_MOR_multi_order(self):
        n = Intrade(self.memNum, self.pw)
        
        orders = []
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='2') )
        
        resp = n.multiOrderRequest(orders, True)

        self.assertEqual(len(resp), 2)

        for o in resp:
            self.assertTrue(o.success)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 2)
        
        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_put_MOR_invalid_contract(self):
        n = Intrade(self.memNum, self.pw)
        
        orders = []
        orders.append( Order(conId='33l1374',side='B', limitPrice='.5',quantity='5') )
        orders.append( Order(conId='3313074',side='B', limitPrice='.5',quantity='2') )
        
        with self.assertRaises(IntradeResponseError):
            resp = n.multiOrderRequest(orders, True)

        
        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_get_trades(self):
        n = Intrade(self.memNum, self.pw)

        trades = n.getTrades(contractId='331374')

        self.assertEqual(len(trades), 4)
        
    def test_cancel_AllInContract_invalid_conId(self): 
        n = Intrade(self.memNum, self.pw)
        
        orders = []
        orders.append( Order(conId='33l1374',side='B', limitPrice='.5',quantity='5') )
        orders.append( Order(conId='3313074',side='B', limitPrice='.5',quantity='2') )
        
        with self.assertRaises(IntradeResponseError):
            resp = n.multiOrderRequest(orders, True)

        with self.assertRaises(IntradeResponseError):
            r = n.cancelAllOrdersInContract('3311374')
            self.assertTrue(r.didCancel)

        
    def test_cancel_AllInContract(self):
        n = Intrade(self.memNum, self.pw)
        
        orders = []
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='2') )
        
        resp = n.multiOrderRequest(orders, True)

        self.assertEqual(len(resp), 2)

        for o in resp:
            self.assertTrue(o.success)

        resp = n.cancelAllOrdersInContract('331374')
        

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_cancel_ByOrderId(self):
            n = Intrade(self.memNum, self.pw)
            
            orders = []
            orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
            orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='2') )
            
            resp = n.multiOrderRequest(orders, True)

            self.assertEqual(len(resp), 2)

            for o in resp:
                self.assertTrue(o.success)

            oids = [o.orderId for o in resp]

            resp = n.cancelOrdersById(oids)

            time.sleep(1)

            orders = n.getOpenOrders()
            self.assertEqual(len(orders), 0)

       
    def test_cancel_all_offers(self):
        n = Intrade(self.memNum, self.pw)

        orders = []
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='2') )
        orders.append( Order(conId='331374',side='S', limitPrice='99',quantity='1') )
        
        resp = n.multiOrderRequest(orders, True)

        self.assertEqual(len(resp), 3)

        for o in resp:
            self.assertTrue(o.success)


        resp = n.cancelAllOffers('331374')

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 2)

        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)


    def test_cancel_all_bids(self):
        n = Intrade(self.memNum, self.pw)

        orders = []
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='2') )
        orders.append( Order(conId='331374',side='S', limitPrice='99',quantity='1') )
        
        resp = n.multiOrderRequest(orders, True)

        self.assertEqual(len(resp), 3)

        for o in resp:
            self.assertTrue(o.success)


        resp = n.cancelAllBids('331374')

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 1)

        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_cancel_orders_in_event(self):
        n = Intrade(self.memNum, self.pw)

        orders = []
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='5') )
        orders.append( Order(conId='331374',side='B', limitPrice='.5',quantity='2') )
        orders.append( Order(conId='331374',side='S', limitPrice='99',quantity='1') )
        
        resp = n.multiOrderRequest(orders, True)

        self.assertEqual(len(resp), 3)

        for o in resp:
            self.assertTrue(o.success)


        resp = n.cancelOrdersInEvent('30848')

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

        r = n.cancelAllOrders()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_get_positions(self):
        n = Intrade(self.memNum, self.pw)

        ps = n.getPositions()

        self.assertEqual(len(ps), 1)

        if len(ps):
            p = ps[0]
            self.assertEqual(p.conId, 331374)
            self.assertEqual(p.quantity, -7)


        ps = n.getPositions('331374')
        self.assertEqual(len(ps), 1)

        if len(ps):
            p = ps[0]
            self.assertEqual(p.conId, 331374)
            self.assertEqual(p.quantity, -7)

    def test_get_messages(self):
        n = Intrade(self.memNum, self.pw)

        msgs = n.getMessages()
        self.assertEqual(len(msgs), 4)


    def test_get_check_messages(self):
        n = Intrade(self.memNum, self.pw)
        
        msgs = n.checkMessages()
        self.assertEqual(msgs, 0)


    def test_get_market_data(self):
        n = Intrade(self.memNum, self.pw)

        md = n.getMarketData()
        

    def test_get_market_data_in_event_class(self):
        n = Intrade(self.memNum, self.pw)

        ec = n.getMarketDataByEventClass('67') #Learn_Financial

    def test_get_price_info(self):
        n = Intrade(self.memNum, self.pw)

        cb = n.getPriceInfo(['331374',])

        

    def test_get_contract_info(self):
        n = Intrade(self.memNum, self.pw)

        ci = n.getContractInfo(['331374',])

    def test_get_closing_price(self):
        n = Intrade(self.memNum, self.pw)

        cp = n.getClosingPrice('331374')


    def test_get_time_and_sales(self):
        n = Intrade(self.memNum, self.pw)

        sales = n.getDailyTimeAndSales('331374');

    
    def test_market_data(self):
        n = Intrade(self.memNum, self.pw)

        md = n.getMarketData()
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntrade)
    unittest.TextTestRunner(verbosity=3).run(suite)
