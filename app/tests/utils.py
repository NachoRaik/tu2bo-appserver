import ast

def register(client,email,username,password):
    return client.post('/register',json={
        'email': email,
        'username': username,
        'password': password
    })

def login(client,email,password):
    return client.post('/login',json={
        'email': email,
        'password': password
    })

def login_and_token_user(client, id = 1):
    response = login(client,"email{}".format(id),"password{}".format(id))
    response = ast.literal_eval(response.data.decode("UTF-8"))
    return response["token"]

def add_video(client,token, user_id, url, author, title, visibility, date):
    return client.post('/users/{}/videos'.format(user_id), headers={"access-token":token}, json={
        'url': url,
        'author': author,
        'title': title,
        'visibility': visibility,
        'date': date
    })

def add_comment_to_video(client, token, video_id, author=None, content=None, timestamp=None):
    request = {}
    if author != None:
        request['author'] = author
    if content != None:
        request['content'] = content
    if timestamp != None:
        request['timestamp'] = timestamp

    return client.post('/videos/{}/comments'.format(video_id),headers={"access-token":token}, json=request)

def get_comments_from_video(client, token, video_id):
    return client.get('/videos/{}/comments'.format(video_id),headers={"access-token":token})

def like_video(client, token, video_id, liked):
    return client.put('/videos/{}/likes'.format(video_id),headers={"access-token":token}, json={
        'liked': liked
    })

def get_videos(client):
    return client.get('/videos')

def get_video(client, token, video_id):
    return client.get('/videos/{}'.format(video_id),headers={"access-token":token})
