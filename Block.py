from MerkleTree import MerkleTree
import json

class Block:
    def __init__(self, nonce, block_header_hash, previous_block_header_hash, transactions, block_height, time):
        self.time = time
        self.nonce = nonce
        self.previous_block_header_hash = previous_block_header_hash
        self.block_header_hash = block_header_hash
        self.transactions = transactions
        self.block_height = block_height
        merkle_tree = MerkleTree()
        merkle_tree.list_of_transactions = self.transactions
        merkle_tree.create_tree
        self.merkle_tree = merkle_tree

    def to_json(self):
        json_object = {"time": self.time,
                                 "nonce": self.nonce,
                                 "block_header_hash": self.block_header_hash,
                                 "previous_block_header_hash": self.previous_block_header_hash,
                                 "transactions": str(self.transactions),
                                 "block_height": self.block_height}

        return json_object

