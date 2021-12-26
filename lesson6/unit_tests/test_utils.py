import unittest
import json

from server.common.utils import get_message, send_message
from server.common.constants import ENCODING, RESPONSE, ACTION, TYPE, TIME, USER, ACCOUNT_NAME


class TestSocket:
    """
    сам не догадался, практически списал
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def recv(self, max_length):
        return json.dumps(self.test_dict).encode(ENCODING)

    def send(self, msg):
        self.encoded_message = json.dumps(self.test_dict).encode(ENCODING)
        self.received_message = msg


class TestUtils(unittest.TestCase):
    test_dict_200 = {RESPONSE: '200'}
    test_dict_400 = {RESPONSE: '400'}
    test_dict_value_error = ''

    test_dict_send = {
        ACTION: 'presence',
        TIME: 1,
        TYPE: 'status',
        USER: {
            ACCOUNT_NAME: 'guest'
        }
    }

    def test_get_message(self):
        test_sock_200 = TestSocket(self.test_dict_200)
        test_sock_400 = TestSocket(self.test_dict_400)
        test_sock_value_error = TestSocket(self.test_dict_value_error)
        self.assertEqual(get_message(test_sock_200), self.test_dict_200)
        self.assertEqual(get_message(test_sock_400), self.test_dict_400)
        self.assertRaises(ValueError, get_message, test_sock_value_error)

    def test_send_message(self):
        test_sock_send = TestSocket(self.test_dict_send)
        send_message(test_sock_send, self.test_dict_send)
        self.assertEqual(test_sock_send.encoded_message, test_sock_send.received_message)


if __name__ == '__main__':
    unittest.main()
