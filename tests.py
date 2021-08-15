import unittest
from spreads import *
from pprint import pprint

class TestProduct(unittest.TestCase):

    def test_make_product(self):
        p1 = Product("BTCUSDT",1648195200000,True)
        self.assertEqual(p1.symbol,"BTCUSDT")
        self.assertEqual(p1.expiry,1648195200000)
        self.assertEqual(p1.does_expire,True)

    def test_update(self):
        new_update = {'ts': 1629016636149, 'sym': 'BTC-31DEC21', 'BidP': 47319.0, 'BidQ': 2000.0, 'AskP': 47329.5, 'AskQ': 13800.0}
        p1 = Product("BTC-31DEC21",1648195200000,True)
        p1.update(new_update)
        self.assertEqual(p1.AskQ,13800.0)
        self.assertEqual(p1.AskP,47329.5)
        self.assertEqual(p1.BidP,47319.0)
        self.assertEqual(p1.BidQ,2000.0)

class TestSpread(unittest.TestCase):

    def test_make_spread(self):
        p1 = Product("BTC-20AUG21",1629446400000,True)
        p2 = Product("BTC-25MAR22",1648195200000,True)

        s1 = Spread(p1,p2)
        u1 = {'ts': 1629016636149, 'sym': 'BTC-20AUG21', 'BidP': 47319.0, 'BidQ': 2000.0, 'AskP': 47329.5, 'AskQ': 13800.0}
        u2 = {'ts': 1629016636137, 'sym': 'BTC-25MAR22', 'BidP': 48255.0, 'BidQ': 2000.0, 'AskP': 48275.5, 'AskQ': 720.0}
        p1.update(u1)
        p2.update(u2)
        s1.update()
        self.assertEqual(s1.BidP,47319.0 - 48275.5)
        self.assertEqual(s1.BidQ,720.0)
        self.assertEqual(s1.symbol,"BTC-20AUG21-BTC-25MAR22")
        
class TestSpreadClient(unittest.TestCase):
    def setUp(self):
        exchange_info = DeribitClient.get_exchange_info("BTC")
        self.exchange_info = list(filter(lambda x: x['instrument_name']!="BTC-PERPETUAL",exchange_info))
        self.symbols = [el['instrument_name'] for el in exchange_info]
        self.symbols_expiries = [(el['instrument_name'],el['expiration_timestamp']) for el in exchange_info]
        self.products = {}
        for sym,expiry in self.symbols_expiries:
            
            self.products[sym] = Product(sym,expiry,does_expire=True)

    def test_make_spread_client(self):
        spreads = SpreadClient(self.products)
        self.assertEqual(self.symbols,list(spreads.futures_products.keys()))
        pprint(spreads.get_spread_matrix())


if __name__ == '__main__':
    unittest.main()