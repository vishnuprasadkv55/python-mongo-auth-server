
from flask import Flask

app = Flask(__name__)



def _initialize_blueprints(app) -> None:
    from .auth.routes import auth
    app.register_blueprint(auth, url_prefix="/auth")

def create_app() -> Flask:
    app = Flask(__name__)
    _initialize_blueprints(app)
    return app