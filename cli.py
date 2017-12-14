import asyncio
import hashlib
from Node import Node
from Transaction import *
from Block import Block
import codecs
import ecdsa
import threading
import multiprocessing
import time
from ecdsa import SigningKey, VerifyingKey
suicide_flag = False
class cli:
    def __init__(self):
     
        sk = SigningKey.generate(curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        self.sk_hex = codecs.encode(sk.to_string(), 'hex').decode("utf-8")
        self.vk_hex = codecs.encode(vk.to_string(), 'hex').decode("utf-8")
        self.loop = asyncio.get_event_loop()
        self.loop.call_soon(self.main)
        self.loop.run_forever()
            
    def main(self):
        console = input("""Welcome to the ITUcoin Node software:
        [0]: Start mining node
        [1]: Start auditing node
        [2]: Make transfer\n""")
        if console == "0":
            port=int(input("Which port would you like to use?"))
            print("Starting mining")
            self.node = Node(self.vk_hex, self.sk_hex, listening_port=port,genesis=True)
            self.loop.call_soon(self.node.main)
        elif console == "1":
            port=int(input("Which port would you like to use?"))
            print("Starting auditing node.")
            self.node = Node(self.vk_hex, self.sk_hex, listening_port=port,genesis=False)
            self.loop.call_soon(self.node.main)
        elif console == "2":
            print("Queueing transaction:")
            self.parse_transaction()
        else:
            print("Command not in list.")
        self.loop.call_soon(self.main)

    async def fibo(self, steps):
        if steps < 2:
            return 1
        else:
            prev = 0
            current = 1
            for i in range(steps):
                temp = current
                current = prev + current
                prev = temp
                print(steps, current)
            return current

    def parse_transaction(self):
        private_key = ""
        from_pub_key = ""
        to_pub_key = ""
        amount = 0
        tx_fee = 0
        message = ""
        success = False
        private_key = input("Input your private key:\n")
        if private_key:
            public_key = input("Input your address:\n")
            if public_key:
                to_public_key = input("Input receiving address:\n")
                if to_public_key:
                    amount = int(input("Input amount to send:\n"))
                    if amount:
                        tx_fee=int(input("Input transaction fee amount. This will pay miners for handling your transaction.\n"))
                        if tx_fee and amount > tx_fee:
                            message=input("Input transaction message. Enter nothing to send default message.\n")
                            if message:
                                self.loop.call_soon(self.send_transaction, private_key, from_pub_key, to_pub_key, amount, tx_fee, message)
                                success = True
                            else:
                                self.loop.call_soon(self.send_transaction, private_key, from_pub_key, to_pub_key, amount, tx_fee, "ITUCOIN")
                                success = True
                        elif tx_fee > amount:
                            print("Error: Transaction fee higher than amount.")
        if success:
            print("Transaction successfully queued.")
        else:
            print("Error: Input needed.")

    def send_transaction(self,private_key, from_pub_key, to_pub_key, amount, tx_fee, message):
        print(message)
        self.node.generate_and_add_transaction(private_key, from_pub_key, to_pub_key, amount, tx_fee, message=message)
        self.loop.call_soon(self.main)

if __name__ == '__main__':
    cli = cli()
