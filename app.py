import os
from flask import Flask
from config import Config
from models import db
from routes import main_bp
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '60 per minute')],
    )
    limiter.init_app(app)

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('1', 'true', 'yes')
    app.run(host=host, port=port, debug=debug)
