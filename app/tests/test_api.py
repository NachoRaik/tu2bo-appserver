import pytest

def test_hello_message(client):
    """ GET /
    Should: return 200 and correct welcome message """

    res = client.get('/')
    assert b'This is the Application Server!' in res.data

def test_ping(client):
    """ GET /ping
    Should: return 200 and correct message """

    res = client.get('/ping')
    assert b'AppServer is ~app~ up!' in res.data