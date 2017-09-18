import time
class Block:
    previous_block_header_hash = b""
    block_header_hash = b""
    merkle_root_hash = b""
    time = 0
    nonce = 0
    nBits = 2
    transactions = []

    def __init__(self, nonce, block_header_hash, previous_block_header_hash, transactions, merkle_root):
        self.time = time.time()
        self.nonce = nonce
        self.previous_block_header_hash = previous_block_header_hash
        self.block_header_hash = block_header_hash
        self.transactions = transactions
        self.merkle_root_hash = merkle_root


