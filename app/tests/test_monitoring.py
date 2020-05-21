class TestMonitoring:
    def test_hello_message(self, client):
        """ GET /
        Should: return 200 and correct welcome message """

        res = client.get('/')
        assert b'This is the Application Server!' in res.data

    def test_ping(self, client):
        """ GET /ping
        Should: return 200 and correct message """

        res = client.get('/ping')
        assert b'AppServer is ~app~ up!' in res.data