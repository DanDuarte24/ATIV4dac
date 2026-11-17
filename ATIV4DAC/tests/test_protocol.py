import socket
import threading
import time
import unittest

from src.protocol import UDPClient, UDPServer


class UDPProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = UDPServer("127.0.0.1", 0)
        cls.server.socket.settimeout(0.2)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)
        cls.client = UDPClient(*cls.server.address, timeout=0.5, retries=2)

    @classmethod
    def tearDownClass(cls):
        cls.server.close()
        cls.thread.join(timeout=1)

    def test_add(self):
        self.assertEqual(self.client.do_operation("add", [7, 5]), 12)

    def test_subtract(self):
        self.assertEqual(self.client.do_operation("subtract", [7, 5]), 2)

    def test_multiply(self):
        self.assertEqual(self.client.do_operation("multiply", [7, 5]), 35)

    def test_divide(self):
        self.assertEqual(self.client.do_operation("divide", [10, 2]), 5)

    def test_echo(self):
        self.assertEqual(self.client.do_operation("echo", ["Olá, UDP!"]), "Olá, UDP!")

    def test_unknown_operation_returns_error(self):
        with self.assertRaisesRegex(RuntimeError, "Operação desconhecida"):
            self.client.do_operation("power", [2, 3])

    def test_division_by_zero_returns_error(self):
        with self.assertRaisesRegex(RuntimeError, "dividir por zero"):
            self.client.do_operation("divide", [10, 0])

    def test_invalid_argument_count_returns_error(self):
        with self.assertRaises(RuntimeError):
            self.client.do_operation("add", [10])


if __name__ == "__main__":
    unittest.main()
