from Server import server
import re
from Block import Block as block
from Transaction import Transaction

class messaging:
    
    def __init__(self, port, address_list, time_out = 20):
        self.known_nodes = address_list
        self.port = port
        self.server = server(port, time_out)
        self.time_out = time_out

    def listen(self):
        print("Listening . . .")
        message, sender = self.server.receive()
        print("Received " + message)
        if message == 'ping':
            self.server.send(sender, b'ping')

        elif message == 'new block':
            print("Sending ok")
            self.server.send(sender, b'ok')
            block = self.receive_block(sender)
            return (message, block, sender)

        elif message == 'new tx':
            self.server.send(sender, b'ok')
            tx = self.receive_tx(sender)
            return (message, tx, sender)

        elif message == 'new node':
            self.server.send(sender, b'ok')
            success = self.receive_nodes(sender)
            #No need to return to Node control, as this can be handled by the messaging obj.

        elif message[0:5] == 'get b':
            block_id = message[5:]
            return(message,"",sender)

        elif message == 'get m':
            return(message,"",sender)

        elif message == 'get n':
            self.send_nodes(sender)
            #No need to return to Node control, as this can be handled by the messaging obj.

        else:
            print("Could not parse message: " + message)
        self.listen()

    def propagate_block(self, block):
        dead_nodes = []
        for address in self.known_nodes:
            self.server.send(address, b'new block')

            message, sender = self.server.receive(address, 'ok')
            print(message)
            if message:
                self.send_block(sender, block)
            else:
                dead_nodes.append(address)
        self.remove(dead_nodes)
        if dead_nodes:
            return False
        else:
            return True

    def propagate_tx(self, transaction):
        dead_nodes = []
        for address in self.known_nodes:
            server.send(address, b'new tx')
            if server.receive(address, 'ok'):
                self.send_tx(transaction)
            else:
                dead_nodes.append(address)
        self.remove(dead_nodes)

    def propagate_node(self, new_node_address):
        self.server.send(new_node_address, b'ping')
        dead_nodes = []
        if server.receive(new_node_address, 'ping'):
            for address in self.known_nodes:
                self.server.send(address, b'new node')
                if self.server.receive(address, 'ok'):
                    self.server.send(address, str(new_node_address).encode())
                else:
                    dead_nodes.append(address)
        else:
            dead_nodes.append(address)
        self.remove(dead_nodes)

    def get_block(self, block_id):
        dead_nodes = []
        for address in self.known_nodes:
            self.server.send(address,('get b '+ str(block_id)).encode())
            return self.receive_block()
        self.remove(dead_nodes)

    def get_mempool(self):
        dead_nodes = []
        for address in self.known_nodes:
            self.server.send(address,'get m')
            if self.server.receive(address, 'ok'):
                self.server.send(address, b'receiving')
                raw_pending_txs = []
                receiving = True
                pending_txs = []
                while receiving:
                    tx = self.receive_tx(address)
                    if tx == 'end transmisison':
                        receiving = False
                    else:
                        server.send(addres, b'ok')
                        pending_txs.append(tx)

                self.remove(dead_nodes)
                return pending_txs
            else:
                dead_nodes.append(address)
        self.remove(dead_nodes)
        return []
    
    def get_nodes(self):
        dead_nodes = []
        for address in self.known_nodes:
            self.server.send(address, b'get n')
            if not self.receive_nodes(address):
                dead_nodes.append(address)
        self.remove(dead_nodes)

    def receive_tx(self,address):
        message, sender = self.server.receive()
        print(message)
        if message and message != "end transmission":
            tx = Transaction.create_from_string(message)
            self.server.send(address, b'ok')
            return tx
        elif message == "end transmission":
            return message
        else:
            return None

    def receive_block(self, address):
        print("Receiving header")
        header, sender = self.server.receive()
        print(header)
        if header:
            self.server.send(sender, b'ok')
            txs = []
            while True:
                print("Receiving tx")
                tx = self.receive_tx(sender)
                if tx and tx != "end transmission":
                    txs.append(tx)
                else:
                    break
            print("Full block received")
            print(header)
            return block.create_from_string(header, txs)

    def receive_nodes(self, address):
        receiving = True
        while receiving:
            message, sender = self.server.receive()
            new_node = (message.split(",")[0], int(message.split(",")[1]))
            if message == "end transmission":
                receiving = False
            elif self.address_filter(message):
                self.known_nodes.append(new_node)
            else:
                return False
            server.send(sender, b'ok')
        return True
    
    def send_nodes(self, address):
        for node_address in self.known_nodes:
            print(node_address)
            self.server.send(address, (node_address[0]+","+str(node_address[1])).encode())
            message, sender = self.server.receive(address, 'ok')
            if message:
                print(message)
                continue
            else:
                print("Timed out when sending nodes")
        self.server.send(address, b"end transmission")

    def send_block_header(self, address, block):
        print("Sending blockheader")
        block_header = block.block_header_string()
        self.server.send(address, block_header.encode())
        message, sender = self.server.receive(address, b'ok')
        print("blockheader: " + message)
        return (message, sender)
         
    def send_block(self, address, block):
        print("Sending block")
        if self.send_block_header(address, block):
            for tx in block.transactions:
                if self.send_transaction(address, tx):
                    continue
                else:
                    return False
            self.server.send(address, b"end transmission")
            return True
            
    def send_mempool(self, address, mempool):
        for pair in mempool.heap:
            tx = pair[1]
            if not self.send_transaction(address, tx):
                return False
        return True

    def send_transaction(self, address, transaction):
        print("Sending tx")
        self.server.send(address, transaction.tx_to_string().encode())
        return self.server.receive(address, "ok")

    def address_filter(self, address_string):
        return re.match('\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b', address_string)

    def remove(self, dead_nodes):
        for node in dead_nodes:
            self.known_nodes.remove(node)
        
        
if __name__ == '__main__':
    m = messaging(10000,[('127.0.0.1',9999)])
    m.listen()
