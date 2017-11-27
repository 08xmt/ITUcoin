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
        data, sender = self.server.receive()
        message = data
        print("Received " + message)
        if message == 'ping':
            print(message, sender)
            self.server.send(sender, b'ping')

        elif message == 'new block':
            self.server.send(sender, b'ok')
            block = self.server.receive_block(sender)
            #TODO: Add block to state

        elif message == 'new tx':
            self.server.send(sender, b'ok')
            tx = self.receive_tx(sender)
            #TODO: Add tx to mempool

        elif message == 'new node':
            self.server.send(sender, b'ok')
            print(self.known_nodes)
            success = self.receive_nodes(sender)
            print(success)

        elif message[0:5] == 'get b':
            block_id = message[5:]
            #TODO: Get block from block_id
            self.send_block(sender, block)

        elif message == 'get m':
            #TODO: Get and implement mempool
            self.send_mempool(sender)

        elif message == 'get n':
            self.send_nodes(sender)

        else:
            print(message)
        print("Listening again . . .")
        self.listen()

    def propagate_block(self, block):
        dead_nodes = []
        for address in self.known_nodes:
            server.send(address, b'new block')
            if server.receive(adress, b'ok'):
                self.send_block(block)
            else:
                dead_nodes.append(address)
        self.remove(dead_nodes)

    def propagate_tx(self, transaction):
        dead_nodes = []
        for address in self.known_nodes:
            server.send(address, b'new tx')
            if server.receive(address, b'ok'):
                self.send_tx(transaction)
            else:
                dead_nodes.append(address)
        self.remove(dead_nodes)

    def propagate_node(self, new_node_address):
        self.server.send(new_node_address, b'ping')
        dead_nodes = []
        if server.receive(new_node_address, b'ping'):
            for address in self.known_nodes:
                self.server.send(address, b'new node')
                if self.server.receive('ok'):
                    self.server.send(address, str(new_node_address).encode())
                else:
                    dead_nodes.append(address)
        else:
            dead_nodes.append(address)
        self.remove(dead_nodes)

    def get_block(self, block_id):
        dead_nodes = []
        for address in self.known_nodes:
            server.send(address,('get b '+ str(block_id)).encode())
            return self.receive_block()
        self.remove(dead_nodes)

    def get_mempool(self):
        dead_nodes = []
        for address in self.known_nodes:
            server.send(address,'get m')
            if server.receive(b'ok'):
                server.send(address, b'receiving')
                raw_pending_txs = []
                receiving = True
                pending_txs = []
                while receiving:
                    tx = self.receive_tx(address)
                    if raw_tx == b'end transmisison':
                        receiving = False
                    else:
                        server.send(addres, b'ok')
                        pending_txs.append(raw_tx) #TODO: Validate transactions before adding them
                return pending_txs
            else:
                dead_nodes.append(address)
        self.remove(dead_nodes)
    
    def get_nodes(self):
        dead_nodes = []
        for address in self.known_nodes:
            server.send(address, 'get n')
            if not self.receive_nodes(address):
                dead_nodes.append(address)
        self.remove(dead_nodes)

    def receive_tx(self,address):
        message, sender = self.server.receive()
        if message:
            tx = Transaction.create_from_string(message)
            print(str(tx))
            server.send(address, b'ok')
        else:
            return None

    def receive_block(self, address):
        raw_header = server.receive()
        if raw_header:
            self.server.send(str(block_id).encode())
            raw_txs = []
            receiving = True
            while receiving:
                raw_tx = server.receive()
                if raw_tx == b'end transmission':
                    receiving = False
                else:
                    self.server.send(address, b'ok') #Acknowledge with tx hash?
                    raw_txs.append(raw_tx) #TODO: Validate transactions before adding them
            return block.construct_from_raw(raw_header, raw_txs)
        else:
            dead_nodes.append(address)

    def receive_nodes(self, address):
        #TODO: Add filter to remove all non-ip addresses
        receiving = True
        while receiving:
            message, sender = self.server.receive()
            print(message.split(",")[0])
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
            message, sender = self.server.receive(address,'ok')
            if message:
                print(message)
                continue
            else:
                print("Timed out when sending nodes")
        self.server.send(address, b"end transmission")

    def send_block_header(self, address, block):
        block_header = str(block)
        server.send(address, block_header)
        return server.receive(block.block_header_hash.encode())
         
    def send_block(self, address, block):
        if self.send_block_header(address, block):
            for tx in block.transactions:
                if self.send_transaction(address, tx):
                    continue
                else:
                    return False
            server.send(address, b"end transmission")
            return True
            
    def send_mempool(self, address, mempool):
        pass

    def send_transaction(self, address, transaction):
        server.send(address, transaction.to_json_string().encode())
        return server.receive(address, b"ok")

    def address_filter(self, address_string):
        return re.match('\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b', address_string)
        
        
if __name__ == '__main__':
    m = messaging(10000,[('127.0.0.1',9999)])
    m.listen()
