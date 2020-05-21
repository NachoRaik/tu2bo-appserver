def add_user(client, username):
    return client.post('/users/', json={
        'username': username
    })

def get_users(client):
    return client.get('/users/')