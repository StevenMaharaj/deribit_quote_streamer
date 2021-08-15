from queue import Queue
from deribit_client import DeribitClient
from spreads import *
from threading import Thread
import json
from typing import List,Dict
from time import sleep
from pprint import pprint

exchange_info = DeribitClient.get_exchange_info("BTC")
exchange_info = list(filter(lambda x: x['instrument_name']!="BTC-PERPETUAL",exchange_info))
symbols = [el['instrument_name'] for el in exchange_info]
symbols_expiries = [(el['instrument_name'],el['expiration_timestamp']) for el in exchange_info]
# symbols.remove("BTC-PERPETUAL")



products = {}
for sym,expiry in symbols_expiries:
    
    products[sym] = Product(sym,expiry,does_expire=True)

spreads = SpreadClient(products)

def producer_single_products_deribit_stream(symbols,q):
    c = DeribitClient(symbols, q)
    c.start_stream()


def consumer_products_deribit_stream(spreads:SpreadClient,q: Queue):
    while True:
        try:
            # print("h")
            queue_item = q.get()
            update = DeribitClient.clean_response(queue_item)
            # print(update)

            spreads.update_spread_matrix(update)


        except KeyError:
            continue


    
def stream_spread_matrix(spreads:SpreadClient):
    while True:
        sleep(1.5)
        pprint(spreads.get_spread_matrix())



q = Queue()

# Make separate thread for the producer
t1 = Thread(target=producer_single_products_deribit_stream, args=(symbols,q,))
t1.daemon = True
t1.start()
t2 = Thread(target=consumer_products_deribit_stream, args=(spreads,q,))
t2.daemon = True
t2.start()


# consumer should  not be run in separate thread so you can stop the program with ctrl+ c
# ctrl+ c only work on the main thread
stream_spread_matrix(spreads)