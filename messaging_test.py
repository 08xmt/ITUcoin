from Server import server
from Transaction import *
from Block import *
from mempool import mempool
from messaging import messaging
import time

def ping(s, a):
    s.send(a,b"ping")
    return s.receive(a, expected_message = "ping")

def new_node(s, a):
    s.send(a, b"new node")
    message, sender = s.receive(a, expected_message = "ok")
    s.send(a, b"127.0.0.1,9998")
    message, sender = s.receive(a, expected_message = "ok")
    s.send(a, b"end transmission")
    return message

def get_node(s, a):
    s.send(a, b"get n")
    node, sender = s.receive(a)
    s.send(a, b"ok")
    message, sender = s.receive(a, expected_message = "end transmission")
    return node

def new_tx(s, a, tx):
    s.send(a, b"new tx")
    message, sender = s.receive(a, expected_message = "ok")
    s.send(a, str(tx).encode())
    message, sender = s.receive(a, expected_message = "ok")

def new_block(s, a, block):
    s.send(a, b"new block")
    message, sender = s.receive(a, expected_message = "ok")
    s.send(a, block.block_header_string().encode())
    message, sender = s.receive(a, expected_message = "ok")
    for tx in block.transaction_list():
        s.send(a, tx.encode())
        message, sender = s.receive(a, expected_message = "ok")
    s.send(a, b"end transmission")

def messaging_new_block_header(m, a, block):
    m.server.send(a, b"new block")
    message, sender = m.server.receive(a, expected_message = "ok")
    m.send_block_header(a, block)
    for tx in block.transaction_list():
        m.server.send(a, tx.encode())
        message, sender = s.receive(a, expected_message = "ok")
    m.server.send(a, b"end transmission")

def messaging_new_block(m, a, block):
    m.server.send(a, b"new block")
    m.server.receive(a, "ok")
    m.send_block(a, block)

def propagate_block(m, a, block):
    m.propagate_block(block)

if __name__ == '__main__':
    a = ("127.0.0.1",10000)
    m = messaging(1001,[a])
 
    tx1 = Transaction(signature="Signature1",
                    input_list=[Input("p_tx_hash", "pubkey", "signature"), Input("p_tx_hash", "pubkey", "signature")],
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

    #tx_mems = mempool(txs=block.transactions)
   
    #print(ping(s, a))

    #print(new_node(s, a))

    #print(get_node(s, a))

    #new_tx(s, a, tx1)

    #messaging_new_block_header(m, a, block)

    #messaging_new_block(m, a, block)

    propagate_block(m, a, block)

