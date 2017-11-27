import unittest
from Node import Node
from Transaction import Transaction, Input, Output
from Block import Block


class Tests(unittest.TestCase):

    def test_getAverageBlockTime(self):
        times = []
        ten_minutes_in_seconds = 10 * 60
        for time in range(0, 2016 * ten_minutes_in_seconds, ten_minutes_in_seconds):
            times.append(time)


        self.assertEqual(Node.getAverageBlockTime(times), ten_minutes_in_seconds)


class TestBlockAndTransactions(unittest.TestCase):

    block_list = []

    def create_blocks(self):
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

        for i in range(0, 3):
            self.block_list.append(Block(213,"headerHas", "otherheaderhash", [tx1, tx2, tx3], i, 132456789))

        block = self.block_list[0]
        print(block.to_string())

        self.assertEqual(10, 12)

if __name__ == '__main__':
    test_classes_to_run = [TestBlockAndTransactions, Tests]

    loader = unittest.TestLoader()
    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)
