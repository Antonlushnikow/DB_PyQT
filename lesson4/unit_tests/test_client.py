import unittest

from client.app.main import check_response
from server.common.constants import RESPONSE


class TestClient(unittest.TestCase):
    ok_str = 'Server has responded with status 200 - OK'
    err_str = 'Server has responded with error 400 - Bad Request'

    def test_no_response(self):
        self.assertRaises(ValueError, check_response, {})

    def test_response_not_200(self):
        self.assertEqual(check_response(
            {RESPONSE: '400'}
        ), self.err_str)

    def test_response_200(self):
        self.assertEqual(check_response(
            {RESPONSE: '200'}
        ), self.ok_str)


if __name__ == '__main__':
    unittest.main()
