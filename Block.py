import time
class Block:
    def __init__(self, nonce, block_header_hash, previous_block_header_hash, transactions, merkle_root, time=time.time()):
        self.time = time
        self.nonce = nonce
        self.previous_block_header_hash = previous_block_header_hash
        self.block_header_hash = block_header_hash
        self.transactions = transactions
        self.merkle_root_hash = merkle_root
        self.merkle_tree = None

    def update_merkle_tree(self):
        pass
