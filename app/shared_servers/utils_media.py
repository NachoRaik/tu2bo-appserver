from datetime import datetime

def validate_visibility(visibility):
    return visibility == "public" or visibility == "private" or visibility == "blocked"

def get_fields(video_id, video):
    return {"author": video["author"], "user_id": video["user_id"], "title": video["title"], "description": video["description"],
     "date": datetime.strftime(video["date"], '%m/%d/%y %H:%M:%S'), "visibility": video["visibility"], "url": video["url"], 
     "thumb": video["thumb"], "id": video_id}