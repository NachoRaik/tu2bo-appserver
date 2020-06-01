from datetime import datetime

def init_db(db):
    db["1"] = {"author": "author1", 
            "user_id": "1", 
            "title": "Big Buck Bunny",
            "description": "Big Buck Bunny tells the story of a giant rabbit with a heart bigger than himself. When one sunny day three rodents rudely harass him, something snaps... and the rabbit ain't no bunny anymore! In the typical cartoon tradition he prepares the nasty rodents a comical revenge.\n\nLicensed under the Creative Commons Attribution license\nhttp://www.bigbuckbunny.org", 
            "date": datetime(2019, 1, 1), 
            "visibility": "public",
            "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", 
            "thumb": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg"}
    db["2"] = {"author": "author1",
            "user_id": "1", 
            "title": "Elephant Dream", 
            "description": "The first Blender Open Movie from 2006", 
            "date": datetime(2019, 1, 2), 
            "visibility": "private",
            "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4", 
            "thumb": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ElephantsDream.jpg"}
    db["3"] = {"author": "author3", 
            "user_id": "2", 
            "title": "For Bigger Blazes",
            "description": "HBO GO now works with Chromecast -- the easiest way to enjoy online video on your TV. For when you want to settle into your Iron Throne to watch the latest episodes. For $35.\nLearn how to use Chromecast with HBO GO and more at google.com/chromecast.", 
            "date": datetime(2019, 1, 3), 
            "visibility": "private",
            "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", 
            "thumb": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerBlazes.jpg"}
    db["4"] = {"author": "author4", 
            "user_id": "3", 
            "title": "For Bigger Escapes",
            "description": "Introducing Chromecast. The easiest way to enjoy online video and music on your TV—for when Batman's escapes aren't quite big enough. For $35. Learn how to use Chromecast with Google Play Movies and more at google.com/chromecast.", 
            "date": datetime(2019, 1, 4), 
            "visibility": "public",
            "url": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4", 
            "thumb": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/ForBiggerEscapes.jpg"}

def validate_visibility(visibility):
    return visibility == "public" or visibility == "private"

def get_fields(video_id, video):
    return {"author": video["author"], "user_id": video["user_id"], "title": video["title"], "description": video["description"],
     "date": datetime.strftime(video["date"], '%m/%d/%y %H:%M:%S'), "visibility": video["visibility"], "url": video["url"], 
     "thumb": video["thumb"], "id": video_id}