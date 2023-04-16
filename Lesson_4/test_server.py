import unittest

from server import get_response


class TestServer(unittest.TestCase):

    def test_get_response_200(self):
        data = get_response({
            'action': 'presence',
            'time': 1,
            'user': {
                'account_name': 'Alex',
                'status': 'Hi!'
            }
        })
        self.assertEqual(data['response'], 200)

    def test_get_response_400(self):
        data = get_response({
            'user': {
                'account_name': 'Alex',
                'status': 'Hi!'
            }
        })
        self.assertEqual(data['response'], 400)

    def test_get_response_404(self):
        data = get_response({
            'action': 'presence',
            'time': 1
            }
        )
        self.assertEqual(data['response'], 404)


if __name__ == '__main__':
    unittest.main()
    