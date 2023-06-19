import unittest

from client import create_presence, get_status


class TestClient(unittest.TestCase):

    def test_create_presence(self):
        data = create_presence()
        data['time'] = 1
        self.assertEqual(data, {
            'action': 'presence',
            'time': 1,
            'user': {
                'account_name': 'Alex',
                'status': 'Hi!'
            }
        })

    def test_code_200(self):
        self.assertEqual(get_status({'response': 200}), '200: OK')

    def test_code_400(self):
        self.assertEqual(get_status({'response': 400}), '400: ERROR')


if __name__ == '__main__':
    unittest.main()