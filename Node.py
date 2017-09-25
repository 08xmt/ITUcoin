import hashlib
from Block import Block
import math


class Node:

    def __init__(self):
        self.blockchain = []
        self.current_nonce = 0
        self.merkle_root = b'N\x16\x9d\xdfG\x9c\x8c\xd9\xb4\xc4^\x02\x84\x18\x170\xcbB\xdf:\x8b\xe8\x92\xa7\xf3y\xbdi\r\xb1\xea\xfa'



    def main(self):
        #Generate genisis_hash, used temporarily as the base
        genesis_hash = self.guess_hash(self.merkle_root, 0, self.merkle_root)
        print("GenesisHas: ", genesis_hash[0])
        genesis_block = Block(genesis_hash[1], genesis_hash[0], genesis_hash[1], [], self.merkle_root)
        self.blockchain.append(genesis_block)
        while True:
            prev_block = self.blockchain[-1]
            correct_block = self.guess_hash(prev_block.block_header_hash, 22, self.merkle_root)
            if correct_block:
                self.current_nonce = 0
                self.create_block(correct_block)


    def create_block(self, correctBlock):
        prev_block = self.blockchain[-1]
        print(prev_block.block_header_hash)
        block = Block(correctBlock[1], correctBlock[0], prev_block.block_header_hash, [], self.merkle_root)
        self.blockchain.append(block)

    def guess_hash(self, previous_block_header_hash, nBits, merkle_root):
        hash_guess = hashlib.sha3_256()
        merkle_root = self.merkle_root #TODO: actual merkle root implementation
        nonce = self.random_nonce()
        hash_guess.update(previous_block_header_hash)
        hash_guess.update(merkle_root)
        hash_guess.update(nonce)
        if self.hash_valid(hash_guess.digest(), nBits):
            return [hash_guess.digest(), nonce]
        else:
            return False

    def random_nonce(self):
        self.current_nonce = self.current_nonce+1
        return str(self.current_nonce).encode()

    def hash_valid(self, hash, nBits):
        byte_idx = math.floor(nBits/8)
        for byte in hash[:byte_idx]:
            if byte > 0:
                return False
        if hash[byte_idx] < 2 ** (8 - (nBits % 8)) - 1:
            return True
        return False

if __name__ == "__main__":
    node = Node()
    node.main()


