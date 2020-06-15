def add_video(client, user_id, url, author, title, visibility, date):
    return client.post('/users/{}/videos'.format(user_id), json={
        'url': url,
        'author': author,
        'title': title,
        'visibility': visibility,
        'date': date
    })

def add_comment_to_video(client, video_id, author=None, content=None, timestamp=None):
    request = {}
    if author != None:
        request['author'] = author
    if content != None:
        request['content'] = content
    if timestamp != None:
        request['timestamp'] = timestamp

    return client.post('/videos/{}/comments'.format(video_id), json=request)

def get_comments_from_video(client, video_id):
    return client.get('/videos/{}/comments'.format(video_id))

def like_video(client, video_id, liked):
    return client.put('/videos/{}/likes'.format(video_id), json={
        'liked': liked
    })

def get_videos(client):
    return client.get('/videos')    
