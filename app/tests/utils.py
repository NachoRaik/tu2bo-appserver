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

def oauth2_login(client, googleToken):
    return client.post('/oauth2login', json={'idToken':googleToken})

def add_video(client, token, user_id, url, author, title, visibility, date):
    return client.post('/users/{}/videos'.format(user_id), headers={"access-token":token}, json={
        'url': url,
        'author': author,
        'title': title,
        'visibility': visibility,
        'date': date
    })

def get_videos_from_user_id(client, token, user_id):
    return client.get('/users/{}/videos'.format(user_id), headers={"access-token":token})

def delete_video(client, token, video_id):
    return client.delete('/videos/{}'.format(video_id), headers={"access-token":token})

def edit_video(client, token, video_id, new_fields):
    return client.patch('/videos/{}'.format(video_id), headers={"access-token":token}, json=new_fields)

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

def get_videos(client, token):
    return client.get('/videos', headers={"access-token":token})

def get_video(client, token, video_id):
    return client.get('/videos/{}'.format(video_id), headers={"access-token":token})

def get_user_profile(client, token, user_id_request):
    return client.get('/users/{}'.format(user_id_request), headers={"access-token":token})

def my_requests(client, token):
    return client.get('/users/my_requests', headers={"access-token":token})

def send_friend_request(client, token, user_id_request):
    return client.post('/users/{}/friend_request'.format(user_id_request), headers={"access-token":token})

def accept_friend_request(client, token, user_id_request):
    return client.post('/users/{}/friends'.format(user_id_request), headers={"access-token":token})

def get_user_friends(client, token, user_id_request):
    return client.get('/users/{}/friends'.format(user_id_request), headers={"access-token":token})

def edit_user_profile(client, token, user_id, profile_pic):
    return client.put('users/{}'.format(user_id), headers={"access-token":token}, json={
        'picture': profile_pic
    })
  
def delete_user_profile(client, token, user_id_request):
    return client.delete('/users/{}'.format(user_id_request), headers={"access-token":token})

def get_stats(client, timestamp=None, num=None):
    query_string = {}
    if timestamp != None:
        query_string['timestamp'] = timestamp
    if num != None:
        query_string['num'] = num
    return client.get('/stats', query_string=query_string)

