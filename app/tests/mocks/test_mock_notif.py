import pytest
from json import loads
from shared_servers.NotificationServer import MockNotificationServer

class TestMockNotificationServer:
    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.mock_notif_server = MockNotificationServer()

    def test_send_notification_success(self):
        """ Register an user should return 200 """

        username = 'user'
        title = 'Notif Title'
        body = 'Notif Body'
        data = {
            'type': 'FRIEND_REQUEST_NOTIFICATION'
        }

        response = self.mock_notif_server.send_notification(username, title, body, data)
        assert response.status_code == 204