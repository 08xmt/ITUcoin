import time
from MerkleTree import MerkleTree


class Block:
    def __init__(self, nonce, block_header_hash, previous_block_header_hash, transactions, time=time.time()):
        self.time = time
        self.nonce = nonce
        self.previous_block_header_hash = previous_block_header_hash
        self.block_header_hash = block_header_hash
        self.transactions = transactions
        merkle_tree = MerkleTree()
        merkle_tree.list_of_transactions = self.transactions
        merkle_tree.create_tree
        self.merkle_tree = merkle_tree

    def __str__(self):
        return str(self.time) + "," + str(self.nonce) + "," + self.previous_block_header_hash + "," + self.block_header_hash


