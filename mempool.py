from heapq import heappush, heappop, heapify

class mempool:
    def __init__(self,txs=[]):
        self.tx_set = set([])
        input_txs = []
        for tx in txs:
            input_txs.append(1./tx.fee_per_byte(),tx)
            self.tx_set.add(tx)

        self.heap = heapify(input_txs)

    def contains(self, item):
        return item in self.tx_set

    def push_tx(self, tx):
        self.tx_set.add(tx)
        heappush(self.heap,(1./tx.fee_per_byte(),tx))

    def pop_tx(self):
        try:
            tx = heappop(self.heap)
            self.tx_set.remove(tx[1])
            return tx[1]
        except:
            return None

    def remove_items(self, tx_list):
        for tx in tx_list:
            if tx in self.tx_set:
                self.heap.remove((1./tx.fee_per_byte(), tx))
                self.tx_set.remove(tx)
        if not isinstance(self.heap, list):
            self.heap = []
        heapify(self.heap)

    def get_transactions(self, amount):
        tx_list = []
        if self.heap:
            for i in range(0,min(amount,len(self.heap))):
                tx = self.pop_tx()
                if tx:
                    tx_list.append(tx[1])
            return tx_list
        else:
            return []

    def threshold_pop_tx(self, size_threshold):
        if(heap[0][1].size() < threshold):
            return self.pop_tx()
        else:
            for tx in self.heap:
                if tx[1].size() < threshold:
                    self.heap.remove(tx)
                    heapify(self.heap)
                    self.tx_set.remove(tx[1])
                    return tx[1]
            return None
