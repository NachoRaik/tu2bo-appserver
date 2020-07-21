import json
from datetime import datetime

TYPE_FRIEND_REQ = 'FRIEND_REQUEST_NOTIFICATION'
TYPE_ACCEPT_FRIEND = 'ACCEPTED_REQUEST_NOTIFICATION'

class NotificationService(object):
    def __init__(self, notification_server):
        self.notification_server = notification_server
    
    def newFriendRequest(self, sender, receiver):
        title = 'Nueva solicitud de amistad'
        body = '{} quiere añadirte como amigo! Ve a ver tus solicitudes para aceptarlo!'.format(sender['username'])
        data = {
            'type': TYPE_FRIEND_REQ
        }
        return self.notification_server.send_notification(receiver['username'], title, body, data)
    
    def friendRequestAccepted(self, accepter, receiver):
        title = 'Amistad aceptada'
        body = '{} y tu ahora son amigos! Ve a ver su perfil!'.format(accepter['username'])
        data = {
            'type': TYPE_ACCEPT_FRIEND,
            'user_id': accepter['id']
        }
        return self.notification_server.send_notification(receiver['username'], title, body, data)
        