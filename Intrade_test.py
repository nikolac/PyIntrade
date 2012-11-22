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
        r = n.cancelAllOrdersForUser()
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

        r = n.cancelAllOrdersForUser()
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
        
        r = n.cancelAllOrdersForUser()
        self.assertTrue(r.didCancel)

        time.sleep(1)

        orders = n.getOpenOrders()
        self.assertEqual(len(orders), 0)

    def test_put_MOR_invalid_contract(self):
        pass
        
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntrade)
    unittest.TextTestRunner(verbosity=3).run(suite)
