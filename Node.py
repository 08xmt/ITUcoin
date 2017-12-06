import hashlib
import codecs
from Block import Block
import math
from Transaction import Transaction, Input, Output
import ecdsa, time
from ecdsa import SigningKey, VerifyingKey
from MerkleTree import MerkleTree
from InputOutput import LoadBlockchain


class Node(object):
    block_height_counter = 0
    block_difficulty = 0 #amount of leading zeroes
    time_threshold_seconds = 60 #Arbitrary number. Arguments can be made for higher or lower value
    expected_time_between_blocks = 10 * 60
    blocks_between_difficulty_check = 2016

    def __init__(self, mining_address, private_key):
        print(private_key)
        print(mining_address)
        self.blockchain = []
        self.current_nonce = 0
        self.blockreward = 50 * 10 ** 8
        self.balance_ledger = {} #address => balance
        self.input_ledger = {} # address => input_dict{input_hash => value}
        self.mining_address = mining_address
        self.mining_sk = SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        self.transaction_hasher = hashlib.sha3_256()
        self.transaction_hash = ""
        first_output = Output(mining_address, self.blockreward, self.mining_sk.sign((str(self.mining_address) + str(self.blockreward)).encode('utf-8')))
        first_transaction = Transaction(self.mining_sk.sign(b"coinbase"),[],[first_output],"coinbase",self.blockreward,coinbase=True)
        self.transactions = [first_transaction]
        self.merkle_tree = MerkleTree(list_of_transactions=self.transactions)
        self.merkle_tree.create_tree()
        self.merkle_root = self.merkle_tree.get_root()

    def main(self):
        #Generate genesis_hash, used temporarily as the base
        genesis_hash = self.guess_hash(self.merkle_root, 0, self.merkle_root)
        print("GenesisHash: ", str(genesis_hash[0]))
        genesis_block = Block(genesis_hash[1], genesis_hash[0], genesis_hash[1], self.transactions, self.block_height_counter, time.time())
        self.block_height_counter += 1;
        self.blockchain.append(genesis_block)
        while True:
            prev_block = self.blockchain[-1]
            correct_block = self.guess_hash(prev_block.block_header_hash, 19, self.merkle_root)
            if correct_block:

                self.current_nonce = 0
                self.add_block(correct_block)

                mining_reward_output = Output(self.mining_address, self.blockreward, self.mining_sk.sign((str(self.mining_address) + str(self.blockreward)).encode('utf-8')))
                mining_reward = Transaction(self.mining_sk.sign(b"coinbase"),[],[mining_reward_output],"coinbase",self.blockreward,coinbase=True)
                for tx in self.transactions:
                    print("Amount: ", tx.amount, "Message: ", tx.message)  
                self.transactions = []
                self.add_transaction(mining_reward)
                print(self.balance_ledger)

    def confirm_block(self, block):
        # First transaction needs to be a coinbase transaction
        if not block.transactions[0].coinbase:
            return False
        # Check if rest of blocks are valid
        for transaction in block.transactions[0:]:
            #TODO: Implement this logic
            pass
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
        self.transactions.append(transaction)
        self.transaction_hasher.update(transaction.get_hash().encode('utf-8'))
        self.transaction_hash = self.transaction_hasher.hexdigest()
        self.merkle_tree = MerkleTree(list_of_transactions=self.transactions)
        self.merkle_tree.create_tree()
        self.merkle_root = self.merkle_tree.get_root()

    def add_block(self, correctBlock):
        prev_block = self.blockchain[-1]
        block = Block(correctBlock[1], correctBlock[0], prev_block.block_header_hash, self.transactions, block_height=self.block_height_counter, time=correctBlock[2])
        self.block_height_counter += 1;
        if self.confirm_block(block):
            for transaction in block.transactions:
                self.update_ledgers(transaction)
            self.blockchain.append(block)

            #Adjust difficulty
            if block.block_height % self.blocks_between_difficulty_check == 0:
                self.adjustDifficulty(block)


    def guess_hash(self, previous_block_header_hash, nBits, merkle_root):
        hash_guess = hashlib.sha3_256()
        nonce = self.random_nonce()
        epoch_time = time.time()
        hash_guess.update(previous_block_header_hash)
        hash_guess.update(merkle_root)
        hash_guess.update(nonce)
        hash_guess.update(str(epoch_time).encode('utf-8'))
        if self.hash_valid(hash_guess.digest(), nBits):
            return [hash_guess.digest(), nonce, epoch_time]
        else:
            return False

    def random_nonce(self):
        self.current_nonce = self.current_nonce+1
        return str(self.current_nonce).encode()

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
        if not self.validate_hash_difficulty(hash):
            return False
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
    def validate_hash_difficulty(self, hash):
        if self.block_difficulty == 0:
            return True

        correct_leading_zeroes = ""
        for i in range(0, self.block_difficulty):
            correct_leading_zeroes += "0"

        hash_difficulty_characters = hash[0:self.block_difficulty]
        return correct_leading_zeroes == hash_difficulty_characters


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
