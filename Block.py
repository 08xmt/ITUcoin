from MerkleTree import MerkleTree
import json
from Transaction import Transaction, Input, Output

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

    @classmethod
    def create_from_string(cls, header_string, transaction_list):
        dict = json.loads(header_string)
        return Block(dict['nonce'],
                     dict['block_header_hash'],
                     dict['previous_block_header_hash'],
                     transaction_list,
                     dict['block_height'],
                     dict['time'])


    def to_dict(self):

        dict = {"time": self.time,
                "nonce": self.nonce,
                "block_header_hash": self.block_header_hash,
                "previous_block_header_hash": self.previous_block_header_hash,
                "transactions": self.transaction_list(),
                "block_height": self.block_height,
                "time": self.time}

        return dict

    def to_string(self):
        return json.dumps(self.to_dict())

    def block_header_string(self):
        dict = {"time": self.time,
                "nonce": self.nonce,
                "block_header_hash": self.block_header_hash,
                "previous_block_header_hash": self.previous_block_header_hash,
                "block_height": self.block_height}
        return json.dumps(dict)

    def transaction_list(self):
        transactions_list = []
        for transaction in self.transactions:
            transactions_list.append(transaction.tx_to_string())

        return transactions_list


if __name__ == '__main__':
    tx1 = Transaction(signature="Signature1",
                      input_list=[Input("p_tx_hash", "pubkey", "signature"),
                                  Input("p_tx_hash", "pubkey", "signature")],
                      output_list=[Output("pubkey", 100, "signature"),
                                   Output("pubkey", 100, "signature"),
                                   Output("pubkey", 100, "signature")],
                      message="This is a message",
                      amount=1000)
    tx2 = Transaction(signature="Signature1",
                      input_list=[Input("p_tx_hash", "pubkey", "signature"),
                                  Input("p_tx_hash", "pubkey", "signature")],
                      output_list=[Output("pubkey", 100, "signature"),
                                   Output("pubkey", 100, "signature"),
                                   Output("pubkey", 100, "signature")],
                      message="This is a message",
                      amount=1000)
    tx3 = Transaction(signature="Signature1",
                      input_list=[Input("p_tx_hash", "pubkey", "signature"),
                                  Input("p_tx_hash", "pubkey", "signature")],
                      output_list=[Output("pubkey", 100, "signature"),
                                   Output("pubkey", 100, "signature"),
                                   Output("pubkey", 100, "signature")],
                      message="This is a message",
                      amount=1000)

    block = Block(213,"headerHas", "otherheaderhash", [tx1, tx2, tx3], 19, 132456789)

    print("block.to_string(): "+block.to_string())
    print()
    print("block.block_header_string(): "+block.block_header_string())
    print()
    print("block.transaction_list_string(): "+str(block.transaction_list()))