import hashlib

class Transaction:
    
    def __init__(self, signature, input_list, output_list, message, amount, locktime = 0):
        self.input_counter = len(input_list)
        self.output_counter = len(output_list)
        self.inputs = input_list
        self.outputs = output_list
        self.locktime = locktime
        self.signature = signature
        self.message = message
        self.amount = amount

    def __str__(self):
        return str(input_counter) + str(output_counter) + str(locktime) + str(self.message)
    
    def get_hash(self):
            
        string_inputs = ""
        string_outputs = ""
        for _input in self.inputs:
            string_inputs += str(_input)
        for output in self.outputs:
            string_outputs += str(output)
        return hashlib.sha3_256(str(self) + string_inputs + string_outputs)
        
class Input:

    def __init__(self, previous_tx, from_public_key):
        self.previous_tx = previous_tx
        self.from_public_key

    def __str__(self):
        return str(self.previous_tx) + str(self.from_public_key)

class Output:

    def __init__(self, to_public_key, value):
        self.to_public_key = to_publick_key
        self.value = value

    def __str__(self):
        return str(self.to_public_key) + str(self.value)
