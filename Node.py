import hashlib
from Block import Block
import math
from Transaction import Transaction, Input, Output
import ecdsa
from ecdsa import SigningKey, VerifyingKey


class Node:

    def __init__(self):
        self.blockchain = []
        self.current_nonce = 0
        self.balance_ledger = {} #address => balance
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

    def transaction_valid(self, transaction):
        return transaction_history_valid(input_list, value) and sig_valid(signature,message,from_public_key)

    def transaction_history_valid(self, input_list, value):
        balance = 0.

        for _input in input_list:
            if not _input in self.balance_ledger:
                return False
            if not self.balance_ledger[_input.from_public_key][_input.previous_tx]:
                return False
            balance += verify_input(_input)
        return balance >= value
    
    def sig_valid(self, signature, message, public_key):
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(sig), message)
        

    def generate_transaction(self, private_key, from_public_key, to_public_key, amount, message = b"ITUCOIN"):
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        sig = sk.sign(message)
        balance = 0.
        input_list = []
        output_list = []

        for prev_tx, prev_tx_value in balance_ledger[from_public_key]:
            input_list.append(Input(prev_tx, from_public_key))
            balance += prev_tx_value
            if balance > amount:
                break
        if balance < amount:
            raise Exception('Balance too low to send transaction.')
        output_list.append(Output(to_public_key, amount))
        if balance - amount > 0:
            output_list.append(Output(from_public_key,balance-amount))

        return Transaction(signature, input_list, output_list, message)
    
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



