#Code inspired by: https://github.com/JaeDukSeo/Simple-Merkle-Tree-in-Python/blob/master/MerkleTrees.py

import hashlib,json
import math
from collections import OrderedDict

class MerkleTree:
    merkle_tree_transactions = OrderedDict()

    def __str__(self):
        return self.get_root()

    def __init__(self, list_of_transactions=None):
        self.list_of_transactions = list_of_transactions
        self.past_transactions = OrderedDict()

    def create_tree(self):
        temp_transactions = []

        #Run through all the transaction and create the merkle tree 
        for index in range(0, len(self.list_of_transactions), 2):
            #construct left node
            node_left = self.list_of_transactions[index]
            node_left_hash =  hashlib.sha3_256(node_left.encode('utf-8'))
            self.past_transactions[self.list_of_transactions[index]] = node_left_hash.hexdigest()

            #construct right node
            if index+1 != len(self.list_of_transactions):
                node_right = self.list_of_transactions[index+1]
                node_right_hash = hashlib.sha3_256(node_right.encode('utf-8'))
                self.merkle_tree_transactions[self.list_of_transactions[index+1]] = node_right_hash.hexdigest()
                temp_transactions.append(node_left_hash.hexdigest() + node_right_hash.hexdigest())

            else:
                temp_transactions.append(node_left_hash.hexdigest())


        if len(self.list_of_transactions) > 1:
            self.list_of_transactions = temp_transactions
            self.create_tree()

    def get_merkle_tree_transactions(self):
        return self.merkle_tree_transactions

    def get_root(self):
        #last_key = self.past_transactions.keys()[-1]
        return next(reversed(self.merkle_tree_transactions))


# Declare the main part of the function to run
if __name__ == "__main__":
# a) Create the new class of Jae_MerkTree
    Jae_Tree = MerkleTree()

    def get_past_transaction(self):
        return self.past_transactions

    def get_root(self):
        #last_key = self.past_transactions.keys()[-1]
        return next(reversed(self.past_transaction))
    
    def conflicting_txs(self, merkle_tree):
        """ Return conflicting transactions between different MerkleTree objects
        Args:
            merkle_tree: A MerkleTree object
        
        Returns:
            A list of conflicting transaction pairs. The pairs in the list contains both values and hash-values.
            Example:
                [('g', '9f2898da52dedaca29f05bcac0c8e43e4b9f7cb5707c14cc3f35a567232cec7c'), ('l', '3e5e3e723953551a2ba2e7c5584bcc4ce407414af1ab2569051e7c9bfa33164d')]

        """
        self_reverse = list(reversed(self.past_transactions.items()))
        other_reverse = list(reversed(merkle_tree.past_transactions.items()))
        self_len = len(self_reverse)
        other_len = len(other_reverse)
        if self_len > other_len:
            return self_reverse[other_len:other_len+math.floor(other_len/2)]
        elif self_len < other_len:
            return other_reverse[self_len:self_len+math.floor(self_len/2)]
        else:
            return self._conflicting_txs_rec(self_reverse, other_reverse, 0)

    def _conflicting_txs_rec(self, self_rev, other_rev, idx):
        length = len(self_rev)
        if self_rev[idx] == other_rev[idx]:
            return []
        if length/2 <= idx:
            return [other_rev[idx]]
        if (idx+1)*2 >= length:
            if idx*2+1 >= length:
                return []
            else:
                return self._conflicting_txs_rec(self_rev, other_rev, idx*2+1)
        return self._conflicting_txs_rec(self_rev, other_rev, idx*2+1) + self._conflicting_txs_rec(self_rev, other_rev, (idx+1)*2)