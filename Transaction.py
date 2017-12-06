import hashlib
import json
import codecs
class Transaction:

    def __init__(self, signature, input_list, output_list, message, amount, locktime = 0, coinbase = False, fee_pr_byte=0):
        self.input_counter = len(input_list)
        self.output_counter = len(output_list)
        self.inputs = input_list
        self.outputs = output_list
        self.locktime = locktime
        if isinstance(signature, bytes):
            self.signature = signature.hex()
        else:
            self.signature = signature
        self.message = message
        self.amount = amount
        self.coinbase = coinbase
        self.fee_pr_byte = fee_pr_byte

    @classmethod
    def create_from_string(cls, transaction_as_string):
        tx = transaction_as_string
        print(tx)
        if isinstance(transaction_as_string, bytes):
            tx = tx.decode()
        tx_dict = json.loads(tx)
        tx_dict = next(iter(tx_dict.values()))
        
        #Last input and output will always be whitespace
        inputs = [Input.load_from_string(i) for i in tx_dict["inputs"].split("|")[:-1]]
        outputs = [Output.load_from_string(i) for i in tx_dict["outputs"].split("|")[:-1]]
        
        tx_dict['inputs'] = inputs
        tx_dict['outputs'] = outputs
            
        return Transaction(signature=tx_dict['signature'],
                           input_list=tx_dict['inputs'],
                           output_list=tx_dict['outputs'],
                           message=tx_dict['message'],
                           amount=tx_dict['amount'],
                           locktime=tx_dict['locktime'],
                           coinbase=tx_dict['coinbase'],
                           fee_pr_byte=tx_dict['fee_pr_byte'])


    def __str__(self):
        return self.tx_to_string()

    def get_hash(self):
        string_inputs = ""
        string_outputs = ""
        hasher = hashlib.sha3_256()
        for _input in self.inputs:
            string_inputs += str(_input)
        for output in self.outputs:
            string_outputs += str(output)
        hasher.update((str(self.locktime) + str(self.message) + str(self.signature) + string_inputs + string_outputs).encode('utf-8'))
        return hasher.hexdigest()

    def get_as_dict(self):
        tx_inputs = []
        tx_outputs = []

        for input in self.inputs:
            tx_inputs.append(input.as_list())

        for output in self.outputs:
            tx_outputs.append(output.as_list())

        transaction_dict = {"locktime": self.locktime, "inputs": tx_inputs, "outputs": tx_outputs, "signature":
                            self.signature, "message": self.message, "amount": self.amount, "coinbase": self.coinbase, "fee_pr_byte": self.fee_pr_byte}
        return {self.get_hash(), transaction_dict}


    def size(self):
        return len(self.tx_to_string.encode('utf-8'))

    def total_fee(self):
        return self.size()*self.fee_pr_byte

    def tx_to_string(self):
        tx_inputs = ""

        for input in self.inputs:
            tx_inputs += input.as_string() + "|"
        
        tx_outputs = ""
        for output in self.outputs:
            tx_outputs += output.as_string() + "|"

        transaction_dict = {"locktime": self.locktime,
                            "inputs": tx_inputs,
                            "outputs": tx_outputs,
                            "signature": self.signature,
                            "message": self.message,
                            "amount": self.amount,
                            "coinbase": self.coinbase,
                            "fee_pr_byte": self.fee_pr_byte}

        hash_string = self.get_hash()

        tx_dict = {hash_string: transaction_dict}
        return json.dumps(tx_dict)


class Input:

    def __init__(self, previous_tx_hash, from_public_key, signature):
        self.previous_tx_hash = previous_tx_hash
        self.from_public_key = from_public_key
        self.signature = signature

    def __str__(self):
        return str(self.previous_tx_hash) + "," + str(self.from_public_key) + "," + str(self.signature)

    @classmethod
    def load_from_string(cls, input_string):
        inputs = input_string.split(',')
        print(input_string)
        return Input(inputs[0], inputs[1], inputs[2])

    def as_string(self):
        return self.__str__()

    def as_list(self):
        return [str(self.previous_tx_hash), str(self.from_public_key), str(self.signature)]

    def get_hash(self):
        hasher = hashlib.sha3_256()
        hasher.update(str(self).encode('utf-8'))
        return hasher.hexdigest()

    def sig_valid(self, public_key):
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(str(self.signature)))


class Output:
    def __init__(self, to_public_key, value, signature, tx_fee = False):
        self.to_public_key = to_public_key
        self.value = value
        if isinstance(signature, bytes):
            self.signature = str(signature.hex())
        else:
            self.signature = signature
        self.tx_fee = tx_fee

    def __str__(self):
        if self.tx_fee:
            return str(True) + "," + str(self.value)+","
        else:
            return str(self.to_public_key) + "," + str(self.value) + "," + str(self.signature)+","

    @classmethod
    def load_from_string(cls, output_string):
        outputs = output_string.split(',')
        if outputs[0] == "True":
            return Output("", int(outputs[1]), "", True)
        else:
            return Output(outputs[0], int(outputs[1]), outputs[2])

    def as_string(self):
        return self.__str__()

    def as_list(self):
        if self.tx_fee:
            return [str(True), str(self.value)]
        else:
            return [str(self.to_public_key), str(self.value), str(self.signature)]

    def get_hash(self):
        hasher = hashlib.sha3_256()
        hasher.update(str(self).encode('utf-8'))
        return hasher.hexdigest()

    def sig_valid(self, public_key):
        vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(str(self.signature)))
