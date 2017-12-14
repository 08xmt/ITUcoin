import asyncio
import hashlib
from Node import Node
from miner import Miner
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
        sk_hex = codecs.encode(sk.to_string(), 'hex').decode("utf-8")
        vk_hex = codecs.encode(vk.to_string(), 'hex').decode("utf-8")
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

        block = Block(213,"headerHas", "otherheaderhash", [tx1, tx2, tx3], 16, 132456789)

        self.miner = Miner(vk_hex, sk_hex, block.transaction_list(),block,("127.0.0.1",10000),10)
        self.loop = asyncio.get_event_loop()
        self.loop.call_soon(self.main)
        self.loop.run_forever()
            
    def main(self):
        console = input("""Welcome to the ITUcoin self.node software:
        [0]: Start mining self.node
        [1]: Start auditing self.node
        [2]: Sync to network
        [3]: Make transfer\n""")
        if console == "0":
            print("Starting mining")
            self.loop.call_soon(self.mine)
        elif console == "1":
            print("Process is alive: " + str(self.mining_process.is_alive()))
        elif console == "2":
            print("Syncing not yet implemented.")
        elif console == "3":
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

    def mine(self):
        self.mining_process = multiprocessing.Process(target=self.miner.main, args=())
        self.mining_process.start()
        print("Waiting 20 to kill process.")
        time.sleep(20)
        self.mining_process.terminate()
        print("Process is alive: " + str(self.mining_process.is_alive()))

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

    def audit(self, daemon):
        pass

    def sync(self):
        pass

if __name__ == '__main__':
    cli = cli()
