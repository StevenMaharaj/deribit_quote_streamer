from queue import Queue
from deribit_client import DeribitClient
from threading import Thread
import json
def clean_response(response:str):
    temp = json.loads(response)

    return temp['params']['data']

def producer(q):
    exchange_info = DeribitClient.get_exchange_info("BTC")
    symbols = [el['instrument_name'] for el in exchange_info]
    symbols.remove("BTC-PERPETUAL")
    # print(symbols)
    # input()
    c = DeribitClient(symbols,q)
    c.start_stream()


def consumer(q:Queue):
    while True:
        try:
            res = q.get()
            print(clean_response(res))
        except KeyError:
            continue

q = Queue()
t1 = Thread(target=consumer, args=(q,))
t2 = Thread(target=producer, args=(q,))
t1.start()
t2.start()