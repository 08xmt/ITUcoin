# Echo server program
import sys
import socket
import time
class server:
    def __init__(self, port, timeout):
        self.port = port
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ("",self.port)
        print('starting up on %s port %s' % self.address)

    def send(self, address, message):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)
        time.sleep(1)
        try:
            self.socket.connect(address)
            self.socket.sendall(message)
        finally:
            self.socket.close()

    def receive(self, address=None, expected_message=""):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Waiting for connection")
        self.socket.bind(self.address)
        self.socket.listen(5)
        connection, client_address = self.socket.accept()
        data = ""
        try:
            print('client connected:', client_address)
            while True:
                data = connection.recv(1024)
                if data:
                    break
        finally:
            connection.close()
            self.socket.close()
            if not expected_message or expected_message == data.decode():
                return (data.decode(), client_address)
            else:
                return ("", client_address)

if __name__ == '__main__':
    s = server(10000,30)
    print(s.receive('127.0.0.1',expected_message="hej"))


"""
def return_block(s, blockhash, blockchain):
    success = False
    if blockhash not in blockchain:
        s.sendall(b"no blockhash")
        s.close()
        return success
    else:
        block = blockchain[blockhash]
        s.sendall(str.encode(block['header']))
        message = block['transactions'].pop(0)
        #data = socket.recv(1024)
        while not success:
            connection, client_address = s.accept()
            try:
                while True:
                    data = connection.recv(1024)
                    if data == str.encode('received ' + message) or data == b'received blockheader':
                        if block['transactions']:
                            message = str.encode(block['transactions'].pop(0))
                        else:
                            message = b"transfer complete"
                            success = True
                        connection.sendall(message)
                        break
                        
            finally:
                connection.close()
        return success
        
 # Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the address given on the command line
#server_name = sys.argv[1]
server_address = ("", 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)
sock.listen(1)
blockchain = {'123456':{'header':'hejhej','transactions':[1,2,3,4]}}

while True:
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('client connected:', client_address)
        while True:
            data = connection.recv(1024)
            string_data = data.decode()
            print('received "%s"' % string_data)
            if 'get-block' in string_data:
                blockhash = string_data.split(" ")[1]
                return_block(connection, '123456', blockchain)
            elif data:
                connection.sendall(data)
            else:
                break
    finally:
        connection.close()
"""
  
