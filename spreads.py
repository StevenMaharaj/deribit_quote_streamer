from typing import List, Dict
from deribit_client import DeribitClient
from queue import Queue


class Product:
    def __init__(self, symbol, expiry, does_expire):
        self.symbol = symbol
        self.expiry = expiry
        self.does_expire = does_expire
        self.BidP = 0.0
        self.BidQ = 0.0
        self.AskP = 0.0
        self.AskQ = 0.0

    def update(self, new_update: dict):
        self.BidP = new_update["BidP"]
        self.BidQ = new_update["BidQ"]
        self.AskP = new_update["AskP"]
        self.AskQ = new_update["AskQ"]


class Spread(Product):
    def __init__(self, product1: Product, product2: Product):
        self.product1 = product1
        self.product2 = product2
        self.symbol = f"{product1.symbol}-{product2.symbol}"

    def best_price(self):
        self.BidP = self.product1.BidP - self.product2.AskP
        self.BidQ = min(self.product1.BidQ, self.product2.AskQ)
        self.AskP = self.product1.AskP - self.product2.BidP
        self.AskQ = min(self.product1.AskQ, self.product2.BidQ)

    def limit_market_price(self):
        self.BidP = self.product1.BidP - self.product2.BidP
        self.BidQ = self.product2.BidQ
        self.AskP = self.product1.AskP - self.product2.AskP
        self.AskQ = self.product2.AskQ

    def update(self):
        self.best_price()

    def to_dict(self) -> dict:
        res = {}
        res["sym"] = self.symbol
        res["BidP"] = self.BidP
        res["BidQ"] = self.BidQ
        res["AskP"] = self.AskP
        res["AskQ"] = self.AskQ
        return res


class SpreadClient:
    def __init__(self, futures_products: Dict[str, Product]) -> None:
        self.futures_products = futures_products
        self.spread_matrix = {}
        self.make_futures_spreads()
        # print(self.spread_matrix)

    def make_futures_spreads(self):
        for i, symi in enumerate(self.futures_products.keys()):
            for j, symj in enumerate(self.futures_products.keys()):
                if i > j:
                    producti = self.futures_products[symi]
                    productj = self.futures_products[symj]
                    if producti.expiry < productj.expiry:
                        sym = f"{symi}-{symj}"
                        self.spread_matrix[sym] = Spread(producti, productj)
                    else:
                        sym = f"{symj}-{symi}"

                        self.spread_matrix[sym] = Spread(productj, producti)
                    self.spread_matrix[sym].update()

        # print(self.spread_matrix)

    def get_spread_matrix(self) -> List[dict]:
        res = []
        for _, el in self.spread_matrix.items():
            res.append(el.to_dict())
        return res

    def update_spread_matrix(self, update: dict):
        sym1 = update['sym']
        self.futures_products[sym1].update(update)
        for symi in self.futures_products.keys():
            if sym1 == symi:
                continue
            if self.futures_products[sym1].expiry < self.futures_products[symi].expiry:
                sym = f"{sym1}-{symi}"
            else:
                sym = f"{symi}-{sym1}"
            self.spread_matrix[sym].update()
            # print(self.spread_matrix[sym].to_dict())
