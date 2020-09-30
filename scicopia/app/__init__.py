from flask import Flask
from flask_bs4 import Bootstrap
from flask_mailman import Mail
from scicopia.flask_config import config

bootstrap = Bootstrap()
mail = Mail()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    with app.app_context():
        from .graph.dashboard import create_dashboard
        app = create_dashboard(app)

        return app
