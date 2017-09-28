#Code inspired by: https://github.com/JaeDukSeo/Simple-Merkle-Tree-in-Python/blob/master/MerkleTrees.py

import hashlib,json
from collections import OrderedDict

class MerkleTree:

    def __inint__(self, list_of_transactions=None):
        self.list_of_transactions = list_of_transactions
        self.past_transactions = OrderedDict()

    def create_tree(self):
        temp_transactions = []
        for index in range(0, self.list_of_transactions, 2):
            #construct left node
            node_left = self.list_of_transaction[index]
            node_left_hash =  hashlib.sha3_256(node_left)
            self.past_transactions[self.list_of_transactions[index]] = node_left_hash.hexdigest()

            #construct right node
            if index+1 != len(self.list_of_transactions):
                node_right = self.list_of_transactions[index+1]
                node_right_hash = hashlib.sha3_256(node_right)
                self.past_transactions[self.list_of_transactions[index+1]] = node_right_hash.hexdigest()
                temp_transactions.append(node_left_hash.hexdigest() + node_right_hash.hexdigest())

            else:
                node_right = ''
                temp_transactions.append(node_left_hash.hexdigest())


        


 
