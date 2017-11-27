from Server import server
from Transaction import *
from Block import *
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

if __name__ == '__main__':
    s = server(9999,20)
    a = ("127.0.0.1",10000)
 
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
   
    #print(ping(s, a))

    #print(new_node(s, a))

    #print(get_node(s, a))

    new_tx(s, a, tx1)
