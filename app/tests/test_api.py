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


def test_(client):
    """ POST /users
    Should: return 200 and correct message """
    userId = '1'
    res = client.post('/users/', json={
        'user_id': userId,
        'username': 'userExample'
    })
    assert res.json.get('id') == 1
    assert res.status_code == 200