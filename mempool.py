from heapq import heappush, heappop, heapify

class mempool:
    def __init__(self,txs=[]):
        self.item_set = set([])
        input_txs = []
        for tx in txs:
            input_txs.append(1./tx.price_of_byte(),tx)
            self.item_set.add(tx)

        self.heap = heapify(input_txs)

    def contains(self, item):
        return item in self.item_set

    def push_tx(self, tx):
        self.item_set.add(tx)
        heappush(self.heap,(1./tx.price_of_byte(),tx))

    def pop_tx(self, tx):
        try:
            tx = heappop(self.heap)
            self.item_set.remove(tx[1])
            return tx[1]
        except:
            return None

    def threshold_pop_tx(self, threshold, tx):
        if(heap[0][1].size() < threshold):
            return self.pop_tx()
        else:
            for tx in self.heap:
                if tx[1].size() < threshold:
                    self.heap.remove(tx)
                    heapify(self.heap)
                    self.item_set.remove(tx[1])
                    return tx[1]
            return None
