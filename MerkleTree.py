#Code inspired by: https://github.com/JaeDukSeo/Simple-Merkle-Tree-in-Python/blob/master/MerkleTrees.py

import hashlib,json
from collections import OrderedDict

class MerkleTree:
    past_transactions = OrderedDict()
    
    def __inint__(self, list_of_transactions=None):
        self.list_of_transactions = list_of_transactions
        #self.past_transactions = OrderedDict()

    def create_tree(self):
        temp_transactions = []
        past_transactions = self.past_transactions

        print("Transactions: ",self.list_of_transactions)
        for index in range(0, len(self.list_of_transactions), 2):
            #construct left node
            node_left = self.list_of_transactions[index]
            node_left_hash =  hashlib.sha3_256(node_left.encode('utf-8'))
            past_transactions[self.list_of_transactions[index]] = node_left_hash.hexdigest()

            #construct right node
            if index+1 != len(self.list_of_transactions):
                node_right = self.list_of_transactions[index+1]
                node_right_hash = hashlib.sha3_256(node_right.encode('utf-8'))
                self.past_transactions[self.list_of_transactions[index+1]] = node_right_hash.hexdigest()
                temp_transactions.append(node_left_hash.hexdigest() + node_right_hash.hexdigest())

            else:
                node_right = ''
                temp_transactions.append(node_left_hash.hexdigest())


        if len(self.list_of_transactions) != 1:
            self.list_of_transactions = temp_transactions

            self.create_tree()

    def get_past_transaction(self):
        return self.past_transactions

    def get_root(self):
        #last_key = self.past_transactions.keys()[-1]
        return next(reversed(self.past_transactions))

"""
# Declare the main part of the function to run
if __name__ == "__main__":

	# a) Create the new class of Jae_MerkTree
	Jae_Tree = MerkleTree()

	# b) Give list of transaction
	transaction = ['a','b','c','d']

	# c) pass on the transaction list 
	Jae_Tree.list_of_transactions = transaction

	# d) Create the Merkle Tree transaction
	Jae_Tree.create_tree()

	# e) Retrieve the transaction 
	past_transaction = Jae_Tree.get_past_transaction()

	# f) Get the last transaction and print all 
	print("First Example - Even number of transaction Merkel Tree")
	print('Final root of the tree : ',Jae_Tree.get_root())
	print(json.dumps(past_transaction, indent=4))
	print("-" * 50) 

	# h) Second example
	print("Second Example - Odd number of transaction Merkel Tree")
	Jae_Tree = MerkleTree()
	transaction = ['a','b','c','d','e']
	Jae_Tree.list_of_transactions = transaction
	Jae_Tree.create_tree()
	past_transaction = Jae_Tree.get_past_transaction()
	print('Final root of the tree : ',Jae_Tree.get_root())
	print(json.dumps(past_transaction, indent=4))
	print("-" * 50)

	# i) Actual Use Case
	print("Final Example - Actuall use case of the Merkle Tree")

	# i-1) Declare a transaction - the ground truth
	ground_truth_Tree = MerkleTree()
	ground_truth_transaction = ['a','b','c','d','e']
	ground_truth_Tree.list_of_transactions = ground_truth_transaction
	ground_truth_Tree.create_tree()
	ground_truth_past_transaction = ground_truth_Tree.get_past_transaction()
	ground_truth_root = ground_truth_Tree.get_root()

	# i-2) Declare a tampered transaction
	tampered_Tree = MerkleTree()
	tampered_Tree_transaction = ['a','b','c','d','f']
	tampered_Tree.list_of_transactions = tampered_Tree_transaction
	tampered_Tree.create_tree()
	tampered_Tree_past_transaction = tampered_Tree.get_past_transaction()
	tampered_Tree_root = tampered_Tree.get_root()

	# i-3) The three company share all of the transaction 
	print('Company A - my final transaction hash : ',ground_truth_root)
	print('Company B - my final transaction hash : ',ground_truth_root)
	print('Company C - my final transaction hash : ',tampered_Tree_root)

	# i-4) Print out all of the past transaction
	print("\n\nGround Truth past Transaction ")
	print(json.dumps(ground_truth_past_transaction, indent=4))
	
	print("\n\nTamper Truth past Transaction ")
	print(json.dumps(tampered_Tree_past_transaction, indent=4))
"""
