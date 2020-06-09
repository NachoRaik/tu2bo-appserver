from flask import Flask, request, Response
from database.db import initialize_db
from config import DevelopmentConfig
from flask_swagger_ui import get_swaggerui_blueprint
import logging

# -- Server setup and config

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'wav'}
JSON_TYPE = "application/json"

# -- Swagger creation
def setup_swaggerui(app):
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "App Server"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    
# -- App creation

def create_app(config=DevelopmentConfig()):
    app = Flask(__name__)
    app.config.from_object(config)
    app.logger.setLevel(logging.DEBUG)

    db = initialize_db(app)

    # -- Routes registration
    from routes import auth, monitoring, users, videos

    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(monitoring.bp_monitor)
    app.register_blueprint(users.bp_users)
    app.register_blueprint(videos.bp_videos)
    setup_swaggerui(app)

    # -- Unassigned endpoints

    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    @app.route('/')
    def hello():
        return "This is the Application Server!"

    @app.route('/friendRequests', methods=['POST'])
    def friend_request():
        return "This endpoint will work for sending invites"

    return app
