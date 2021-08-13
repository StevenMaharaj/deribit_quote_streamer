from typing import List,Dict
from deribit_client import DeribitClient
from queue import Queue

class Product:
    def __init__(self,symbol,expiry,does_expire):
        self.symbol = symbol
        self.expiry = expiry
        self.does_expire = does_expire
        self.BidP = 0.0
        self.BidQ = 0.0
        self.AskP = 0.0
        self.AskQ = 0.0

    def update(self,new_update:dict):
        self.BidP = new_update["BidP"]
        self.BidQ = new_update["BidQ"]
        self.AskP = new_update["AskP"]
        self.AskQ = new_update["AskQ"]
        
class Spread(Product):
    def __init__(self,product1:Product,product2:Product):
        self.product1 = product1
        self.product2 = product2

    def best_price(self):
        self.BidP = self.product1.BidP - self.product2.AskP
        self.BidQ = min(self.product1.BidQ, self.product2.AskQ)
        self.AskP = self.product1.AskP - - self.product2.BidP
        self.AskQ = min( self.product1.AskQ,self.product2.BidQ)
    
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
    def __init__(self,futrue_sproducts:Dict[str,Product]) -> None:
        self.futrue_sproducts = futrue_sproducts
        self.spread_matrix = {}
        self.make_futures_spreads()
        # print(self.spread_matrix)


    
    def make_futures_spreads(self):
        i = 0
        j = 0
        for symi in self.futrue_sproducts.keys():
            for symj in self.futrue_sproducts.keys():
                if i > j+1:
                    # print(i,j)
                    producti = self.futrue_sproducts[symi]
                    productj = self.futrue_sproducts[symj]
                    if producti.expiry < productj.expiry:
                        sym = f"{producti} - {productj}"
                        self.spread_matrix[sym] = Spread(producti,productj)
                    else:
                        sym = f"{productj} - {producti}"

                        self.spread_matrix[sym] = Spread(productj,producti)
            
                j += 1
            i+=1
        print(self.spread_matrix)

    


    def get_spread_matrix(self) -> List[dict]:
        res = []
        for _,el in self.spread_matrix.items():
            res.append(el.to_dict())
        return res

    def update_spread_matrix(self,update:dict):
        sym1 = update['sym']
        self.futrue_sproducts[sym1].update(update)
        for symi in self.futrue_sproducts.keys():
            if self.futrue_sproducts[sym1].expiry < self.futrue_sproducts[symi].expiry:
                sym = f"{sym1} - {symi}"
            else:
                sym = f"{symi} - {sym1}"
            self.spread_matrix[sym].update()
            print(self.spread_matrix[sym].to_dict())






        


