from Server import server
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
    message, sender = s.receive(a)
    print(message)
    s.send(a, b"ok")
    message, sender = s.receive(a, expected_message = "end transmission")
    print(message)

def new_tx(s, a, tx):
    s.send(a, b"new tx")
    message, sender = s.receive(a, expected_message = "ok")
    s.send(a, tx.to_json_string().encode())

if __name__ == '__main__':
    s = server(9999,20)
    a = ("127.0.0.1",10000)
    
    #print(ping(s, a))

    #print(new_node(s, a))

    #print(get_node(s, a))


