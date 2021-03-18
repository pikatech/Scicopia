import os

from .app import create_app


def wsgi():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    return app

if __name__ == "scicopia.flask_main":
	app = create_app(os.getenv('FLASK_CONFIG') or 'default')
