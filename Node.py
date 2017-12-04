import hashlib
import codecs
from Block import Block
import math
from Transaction import Transaction, Input, Output
import ecdsa, time
from ecdsa import SigningKey, VerifyingKey
from MerkleTree import MerkleTree
from InputOutput import LoadBlockchain
from mempool import mempool
from messaging import messaging


class Node(object):
    block_height_counter = 0
    block_difficulty = 0 #amount of leading zeroes
    time_threshold_seconds = 60 #Arbitrary number. Arguments can be made for higher or lower value
    expected_time_between_blocks = 10 * 60
    blocks_between_difficulty_check = 2016

    def __init__(self, mining_address, private_key,listening_port=10000):
        self.blockchain = []
        self.blockreward = 50 * 10 ** 8
        self.balance_ledger = {} #address => balance
        self.input_ledger = {} # address => input_dict{input_hash => value}
        self.mining_address = mining_address
        self.mining_sk = SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        self.transaction_hasher = hashlib.sha3_256()
        self.mempool = mempool()
        self.messaging = messaging(10000,[])

    def main(self):
        while True:
            message, payload, sender = self.messaging.listen()
            if message == 'new block':
                if valid_block(payload):
                    if self.mining_process.is_alive():
                        self.mining_process.terminate()
                    self.add_block(payload)
                    self.mempool.remove_items(payload.transaction_list())
            elif message == 'new tx':
                if transaction_valid(payload):
                    self.add_transaction()
            elif message[0:5] == 'get b':
                self.messaging.send_block(sender, get_max_block)
            elif message == 'get m':
                self.messaging.send_mempool(sender, self.mempool)

    def valid_block(self, block):
        # First transaction needs to be a coinbase transaction
        if not block.transactions[0].coinbase:
            return False
        # Check if rest of blocks are valid
        for transaction in block.transactions[0:]:
            if not transaction_valid(transaction):
                return False
        return True

    def update_ledgers(self, transaction):
        for _input in transaction.inputs:
            value = self.input_ledger[_input.from_public_key].pop(_input.previous_tx_hash)
            if _input.from_public_key in self.balance_ledger:
                self.balance_ledger[_input.from_public_key] -= value
        for _output in transaction.outputs:
            if _output.to_public_key in self.balance_ledger:
                self.balance_ledger[_output.to_public_key] += _output.value
            else:
                self.balance_ledger[_output.to_public_key] = _output.value
                print(_output.value, _output.to_public_key)
            new_input = Input(transaction.get_hash(), _output.to_public_key, _output.signature) #TODO: Check if this is the correct signature to use.
            if not _output.to_public_key in self.input_ledger:
                self.input_ledger[_output.to_public_key] = {}
            self.input_ledger[_output.to_public_key][new_input.get_hash()] = _output.value

    def add_transaction(self, transaction):
        self.mempool.push_tx(transaction)

    def add_block(self, block):
        self.block_height_counter += 1;
        if self.valid_block(block):
            for transaction in block.transactions:
                self.update_ledgers(transaction)
            self.blockchain.append(block)

            #Adjust difficulty
            if block.block_height % self.blocks_between_difficulty_check == 0:
                self.adjustDifficulty(block)

    def transaction_valid(self, transaction, from_public_key):
        return transaction_history_valid(transaction.input_list, transaction.output_list, transaction.amount, from_public_key) and sig_valid(signature,message,from_public_key)

    def transaction_history_valid(self, input_list, output_list, value, from_public_key):
        balance_in = 0
        balance_out = 0

        for _input in input_list:
            if not _input.from_public_key in self.input_ledger:
                return False
            if not _input.sig_valid(from_public_key):
                return False
            if not _input.get_hash() in self.input_ledger[_input.from_public_key]:
                return False
            balance_in += self.input_ledger[_input.from_public_key[_input.get_hash()]]
        if balance_in < value:
            return False

        for _output in output_list:
            if not _output.sig_valid(from_public_key):
                return False
            balance_out += _output.value
            if balance_out > balance_in:
                return False
        return True

    def sig_valid(self, signature, message, public_key):
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(sig), message)

    def generate_transaction(self, private_key, from_public_key, to_public_key, amount, tx_fee, message = b"ITUCOIN"):
        sk = SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        sig = sk.sign(message)
        balance = 0.
        input_list = []
        output_list = []

        for prev_tx, prev_tx_value in balance_ledger[from_public_key]:
            tx_sig = sk.sign(str(prev_tx) + str(from_public_key))
            _input = Input(prev_tx, from_public_key, tx_sig)
            input_list.append(_input)
            balance += prev_tx_value
            if balance + tx_fee > amount:
                break
        if balance < amount:
            raise Exception('Balance too low to send transaction.')

        sent_sig = sk.sign(str(to_public_key), str(amount))
        output_list.append(Output(to_public_key, amount,sent_sig))
        if balance - amount > 0:
            self_sig = sk.sign(str(from_public_key), str(balance-amount))
            output_list.append(Output(from_public_key,balance-amount,self_sig))
        fee_sig = sk.sign(str(True) + str(self.value))
        output_list.append(Output(from_public_key, tx_fee, fee_sig))

        return Transaction(signature, input_list, output_list, message)

    def generate_and_add_transaction(self, private_key, from_public_key, to_public_key, amount, tx_fee, message = b"ITUCOIN"):
        tx = self.generate_transaction(private_key, from_public_key, to_public_key, amount, tx_fee, message)
        self.add_transaction(tx)

    def hash_valid(self, hash, nBits):
        byte_idx = math.floor(nBits/8)
        for byte in hash[:byte_idx]:
            if byte > 0:
                return False
        if hash[byte_idx] < 2 ** (8 - (nBits % 8)) - 1:
            return True
        return False

    """
    difficulty adjustment methods
    """

    def adjustDifficulty(self, c_block):
        average_time = self.getAverageBlockTime(self.getBlockTimesList(c_block))
        if average_time > self.expected_time_between_blocks+self.time_threshold_seconds:
            self.block_difficulty -= 1 #Make it easier
        elif average_time < self.expected_time_between_blocks-self.time_threshold_seconds:
            self.block_difficulty += 1 #make it harder
        return self.block_difficulty


    def getBlockTimesList(self, c_block):
        io = LoadBlockchain()
        height = c_block.block_height
        times = []
        for block_number in range(height - self.blocks_between_difficulty_check, height):
            block = io.get_block(block_number)
            times.append(block.time)

        return times

    @classmethod
    def getAverageBlockTime(self, times):
        time_sum = 0
        for index in range(len(times)-1):
            time1 = times[index]
            time2 = times[index+1]

            time_sum += (time2-time1)

        average_time = int(round(time_sum/self.blocks_between_difficulty_check))
        return average_time


if __name__ == "__main__":
    sk = SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    sk_hex = codecs.encode(sk.to_string(), 'hex').decode("utf-8")
    vk_hex = codecs.encode(vk.to_string(), 'hex').decode("utf-8")
    node = Node(vk_hex, sk_hex)

    node.main()
