import hashlib

class Transaction:
    
    def __init__(self, signature, input_list, output_list, message, amount, locktime = 0, coinbase = False):
        self.input_counter = len(input_list)
        self.output_counter = len(output_list)
        self.inputs = input_list
        self.outputs = output_list
        self.locktime = locktime
        self.signature = signature
        self.message = message
        self.amount = amount
        self.coinbase = coinbase

    def __str__(self):
        return str(self.locktime) + str(self.message) + str(self.signature)
    
    def get_hash(self):
            
        string_inputs = ""
        string_outputs = ""
        hasher = hashlib.sha3_256()
        for _input in self.inputs:
            string_inputs += str(_input)
        for output in self.outputs:
            string_outputs += str(output)
        hasher.update((str(self) + string_inputs + string_outputs).encode('utf-8'))
        return hasher.digest()
        
class Input:

    def __init__(self, previous_tx_hash, from_public_key, signature):
        self.previous_tx_hash = previous_tx_hash
        self.from_public_key = from_public_key
        self.signature = signature

    def __str__(self):
        return str(self.previous_tx_hash) + str(self.from_public_key) + str(self.signature)

    def get_hash(self):
        hasher = hashlib.sha3_256()
        hasher.update(str(self).encode('utf-8'))
        return hasher.digest()

    def sig_valid(self, public_key):
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(str(self.signature)))

class Output:

    def __init__(self, to_public_key, value, signature, tx_fee = False):
        self.to_public_key = to_public_key
        self.value = value
        self.signature = signature
        self.tx_fee = tx_fee

    def __str__(self):
        if self.tx_fee:
            return str(True) + str(self.value)
        else:
            return str(self.to_public_key) + str(self.value) + str(self.signature)

    def get_hash(self):
        hasher = hashlib.sha3_256()
        hasher.update(str(self).encode('utf-8'))
        return hasher.digest()
 
    def sig_valid(self, public_key):
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(str(self.signature)))
