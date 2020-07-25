from flask import Response
import json
import requests
from utils.flask_utils import make_flask_response

class NotificationServer():

    def __init__(self, url = 'no-host'):
        self.url = url

    def send_notification(self, username, title, body, data):
        request_body = {
            "username": username,
            "notification": {
                "title": title,
                "body": body,
                "data": data
            }
        }
        response = requests.post(f'{self.url}/notifications', json=request_body)
        return make_flask_response(response)

    def __str__(self):
        return "url => {}".format(self.url)

# --- Mocks

class MockNotificationServer(NotificationServer):
    def __init__(self):
        super().__init__()

    def send_notification(self, username, title, body, data):
        return Response('', 204)
