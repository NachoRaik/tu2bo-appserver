from flask import Flask, request, Response
from database.db import initialize_db
from config import DevelopmentConfig

# -- Server setup and config

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'wav'}
JSON_TYPE = "application/json"

# -- App creation

def create_app(config=DevelopmentConfig()):
    app = Flask(name)
    app.config.from_object(config)
    db = initialize_db(app)

    import users, monitoring

    app.register_blueprint(users.bp_users)
    app.register_blueprint(monitoring.bp_monitor)
    
    # -- Unassigned endpoints
    @app.route('/')
    def hello():
        return "This is the Application Server!"

    @app.route('/friendRequests', methods=['POST'])
    def friend_request():
        return "This endpoint will work for sending invites"

    return app