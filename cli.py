import asyncio
import hashlib
from Node import Node
import codecs
import ecdsa
import threading
from ecdsa import SigningKey, VerifyingKey

def main(loop, node):
    console = input("""Welcome to the ITUcoin node software:
    [0]: Start mining node
    [1]: Start auditing node
    [2]: Sync to network
    [3]: Make transfer\n""")
    if console == "0":
        daemon = True
        console = input("Run miner as daemon[Y/n]\n")
        if console == "n":
            daemon = False
        loop.call_soon(mine, node, daemon)
    elif console == "1":
        print("Auditing not yet implemented.")
    elif console == "2":
        print("Syncing not yet implemented.")
    elif console == "3":
        print("Transactions not yet implemented.")
    else:
        print("Command not in list.")
    loop.call_soon(main, loop, node)

async def fibo(steps):
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

def mine(node, daemon):
    mining_thread = threading.Thread(target=node.main, args=())
    mining_thread.daemon = daemon
    mining_thread.start()

def send_transaction(pub_key, value):
    pass

def audit(node, daemon):
    pass

def sync(node):
    pass

if __name__ == '__main__':

    sk = SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    sk_hex = codecs.encode(sk.to_string(), 'hex').decode("utf-8")
    vk_hex = codecs.encode(vk.to_string(), 'hex').decode("utf-8")
    node = Node(vk_hex, sk_hex)

    loop = asyncio.get_event_loop()
    loop.call_soon(main, loop, node)
    loop.run_forever()
    
