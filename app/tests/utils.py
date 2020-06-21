import ast

def register_user(client, email=None, username=None, password=None):
    request = {}
    if email != None: request['email'] = email
    if username != None: request['username'] = username
    if password != None: request['password'] = password

    return client.post('/register', json=request)

def login_user(client, email=None, password=None):
    request = {}
    if email != None: request['email'] = email
    if password != None: request['password'] = password

    return client.post('/login', json=request)

def parse_login(response):
    parsed_res = ast.literal_eval(response.data.decode("UTF-8"))
    return parsed_res['token'], parsed_res['user']

def login_and_token_user(client, id = 1):
    response = login_user(client, "email{}".format(id), "password{}".format(id))
    token, user = parse_login(response)
    return token

def add_video(client, token, user_id, url, author, title, visibility, date):
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

    return client.post('/videos/{}/comments'.format(video_id), headers={"access-token":token}, json=request)

def get_comments_from_video(client, token, video_id):
    return client.get('/videos/{}/comments'.format(video_id), headers={"access-token":token})

def like_video(client, token, video_id, liked):
    return client.put('/videos/{}/likes'.format(video_id), headers={"access-token":token}, json={
        'liked': liked
    })

def get_videos(client):
    return client.get('/videos')

def get_video(client, token, video_id):
    return client.get('/videos/{}'.format(video_id), headers={"access-token":token})

def get_user_profile(client,token, user_id_request):
    return client.get('/users/{}'.format(user_id_request), headers={"access-token":token})

def my_requests(client,token):
    return client.get('/users/my_requests', headers={"access-token":token})

def send_friend_request(client,token, user_id_request):
    return client.post('/users/{}/friend_request'.format(user_id_request), headers={"access-token":token})
