import unittest
from server.common.constants import RESPONSE, ACTION, TIME, TYPE, USER, ACCOUNT_NAME
from server import check_message


class TestServer(unittest.TestCase):
    err_dict = {RESPONSE: '400'}

    def test_no_action(self):
        self.assertEqual(check_message(
            {
                TIME: 2,
                TYPE: 'status',
                USER: {
                    ACCOUNT_NAME: 'guest'
                }
            }
        ), self.err_dict)

    def test_action_not_presence(self):
        self.assertEqual(check_message(
            {
                ACTION: 'presencde',
                TIME: 2,
                TYPE: 'status',
                USER: {
                    ACCOUNT_NAME: 'guest'
                }
            }
        ), self.err_dict)

    def test_no_time(self):
        self.assertEqual(check_message(
            {
                ACTION: 'presence',
                TYPE: 'status',
                USER: {
                    ACCOUNT_NAME: 'guest'
                }
            }
        ), self.err_dict)

    def test_no_user(self):
        self.assertEqual(check_message(
            {
                ACTION: 'presence',
                TIME: 2,
                TYPE: 'status'
            }
        ), self.err_dict)

    def test_user_not_guest(self):
        self.assertEqual(check_message(
            {
                ACTION: 'presence',
                TIME: 2,
                TYPE: 'status',
                USER: {
                    ACCOUNT_NAME: 'gest'
                }
            }
        ), self.err_dict)


if __name__ == '__main__':
    unittest.main()
