import hashlib
import codecs
from Block import Block
import math
from Transaction import Transaction, Input, Output
import ecdsa, time
from ecdsa import SigningKey, VerifyingKey
from MerkleTree import MerkleTree
from mempool import mempool
from miner import Miner
from messaging import messaging
from InputOutput import Input_Output
import multiprocessing


class Node(object):
    block_difficulty = 0 #amount of leading zeroes
    time_threshold_seconds = 60 #Arbitrary number. Arguments can be made for higher or lower value
    expected_time_between_blocks = 10 * 60
    blocks_between_difficulty_check = 2016

    def __init__(self, mining_address, private_key,listening_port=10000, genesis=False):
        self.block_height_counter = 0
        self.blockchain = []
        self.blockreward = 50 * 10 ** 8
        self.balance_ledger = {} #address => balance
        self.input_ledger = {} # address => input_dict{input_hash => value}
        self.mining_address = mining_address
        self.mining_sk = SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        self.transaction_hasher = hashlib.sha3_256()
        self.mempool = mempool()
        self.listening_port = listening_port
        self.messaging = messaging(self.listening_port,[])
        self.io = Input_Output()
        self.block_difficulty = 12
        self.get_state()
        if genesis:
            self.mine(self.mempool.get_transactions(10))

    def main(self):
        while True:
            message, payload, sender = self.messaging.listen()
            if message == 'new block':
                isValid = self.valid_block(payload)
                print(isValid)
                print(payload.block_header_string())
                if isValid:
                    if self.mining_process.is_alive():
                        self.mining_process.terminate()
                    self.add_block(payload)
                    self.mempool.remove_items(payload._transaction_list())
                    self.get_state()
                    self.mine(self.mempool.get_transactions(10))
            elif message == 'new tx':
                if self.transaction_valid(payload):
                    self.add_transaction()
            elif message[0:5] == 'get b':
                block_id = int(message[6:])
                block = self.io.get_block(block_id)
                self.messaging.send_block(sender, block)
            elif message == 'get m':
                self.messaging.send_mempool(sender, self.mempool)

    def mine(self, transactions):
        last_block = self.blockchain[-1]
        self.miner = Miner(self.mining_address, self.mining_sk, transactions, last_block, ("127.0.0.1",self.listening_port),self.block_difficulty)
        self.mining_process = multiprocessing.Process(target=self.miner.main, args=())
        self.mining_process.start()

    def get_state(self):
        try:
            newest_block = self.io.get_newest_block()
        except:
            print("Genesis")
            self.genesis()
            newest_block = self.blockchain[0]
        newest_known_block = self.messaging.get_block(2 ** 64-1) #Request high blocknumber to get highest known block
        if not newest_known_block:
            self.blockchain.append(newest_block)
            newest_known_block = newest_block

        blocks_behind = newest_known_block.block_height - newest_block.block_height
        if blocks_behind > 0:
            for i in range(newest_block.block_height, newest_known_block.block_height):
                block = self.messaging.get_block(i)
                if block:
                    self.add_block(block)
        transactions = self.messaging.get_mempool()
        for tx in transactions:
            if not self.mempool.contains(tx):
                self.mempool.push_tx(tx)
    
    def valid_block(self, block):
        # First transaction needs to be a coinbase transaction
        print("Testing block validity")
        print(block.block_height)
        if block.block_height == 0 and block.block_header_hash == "genesis":
            return True

        if not block.transactions[0].coinbase or block.transactions[0].amount != self.blockreward:
            print("First reward not coinbase or wrong blockreward")
            return False

        #Test hash difficulty
        if not self.validate_hash_difficulty(block.block_header_hash):
            print("Not valid hash difficulty")
            return False
        # Check if rest of blocks are valid
        print("Testing transaction validity")

        for transaction in block.transactions[1:]:
            print(transaction.tx_to_string())
            if not self.transaction_valid(transaction,self.mining_address):
                print("Invalid transaction")
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
            new_input = Input(transaction.get_hash(), _output.to_public_key, _output.signature) #TODO: Check if this is the correct signature to use.
            if not _output.to_public_key in self.input_ledger:
                self.input_ledger[_output.to_public_key] = {}
            self.input_ledger[_output.to_public_key][new_input.get_hash()] = _output.value

    def add_transaction(self, transaction):
        self.mempool.push_tx(transaction)

    def add_block(self, block):
        if self.valid_block(block):

            for transaction in block.transactions:
                self.update_ledgers(transaction)
            self.io.insert_blocks([block])
            self.blockchain.append(block)
            self.block_height_counter += 1;

            #Adjust difficulty
            if block.block_height % self.blocks_between_difficulty_check == 0:
                self.adjustDifficulty(block)

    def transaction_valid(self, transaction, from_public_key):
        return self.transaction_history_valid(transaction.inputs, transaction.outputs, transaction.amount, from_public_key) and self.sig_valid(signature,message,from_public_key)

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

    def sig_valid(self, sig, message, public_key):
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(sig), message)

    def generate_transaction(self, private_key, from_public_key, to_public_key, amount, tx_fee, message = b"ITUCOIN"):
        sk = SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        sig = sk.sign(message)
        balance = 0.
        input_list = []
        output_list = []

        for prev_tx, prev_tx_value in self.balance_ledger[from_public_key]:
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

        return Transaction(sig, input_list, output_list, message)

    def generate_and_add_transaction(self, private_key, from_public_key, to_public_key, amount, tx_fee, message = b"ITUCOIN"):
        tx = self.generate_transaction(private_key, from_public_key, to_public_key, amount, tx_fee, message)
        self.add_transaction(tx)


    """
    difficulty adjustment methods
    """
    def validate_hash_difficulty(self, hex_str):
        hash = bytearray.fromhex(hex_str)
        byte_idx = math.floor(self.block_difficulty/8)
        for byte in hash[:byte_idx]:
            if byte > 0:
                return False
        if hash[byte_idx] < 2 ** (8 - (self.block_difficulty % 8)) - 1:
            return True
        return False
        if self.block_difficulty == 0:
            return True
        """
        correct_leading_zeroes = ""
        for i in range(0, self.block_difficulty):
            correct_leading_zeroes += "0"
        print(hash)
        print(correct_leading_zeroes)
        hash_difficulty_characters = hash[0:self.block_difficulty]
        return correct_leading_zeroes == hash_difficulty_characters
        """

    def adjust_difficulty(self, c_block):
        average_time = self.getAverageBlockTime(self.getBlockTimesList(c_block))
        if average_time > self.expected_time_between_blocks+self.time_threshold_seconds:
            self.block_difficulty -= 1 #Make it easier
        elif average_time < self.expected_time_between_blocks-self.time_threshold_seconds:
            self.block_difficulty += 1 #make it harder
        return self.block_difficulty

    def getBlockTimesList(self, c_block):
        height = c_block.block_height
        times = []
        for block_number in range(height - self.blocks_between_difficulty_check, height):
            block = self.io.get_block(block_number)
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
    
    def genesis(self):
        first_output = Output(self.mining_address, self.blockreward, self.mining_sk.sign((str(self.mining_address) + str(self.blockreward)).encode('utf-8')))
        first_transaction = Transaction(self.mining_sk.sign(b"coinbase"),[],[first_output],"coinbase",self.blockreward, "",coinbase=True)
        transactions = [first_transaction]
        tree = MerkleTree(list_of_transactions=transactions)
        tree.create_tree()
        root = tree.get_root()
        genesis_block = Block(0, "genesis", "", transactions, self.block_height_counter, time.time())
        self.add_block(genesis_block);
        


if __name__ == "__main__":
    sk = SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    sk_hex = codecs.encode(sk.to_string(), 'hex').decode("utf-8")
    vk_hex = codecs.encode(vk.to_string(), 'hex').decode("utf-8")
    node = Node(vk_hex, sk_hex, genesis=True)

    node.main()
