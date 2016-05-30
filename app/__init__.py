from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user,\
    current_user


db = SQLAlchemy()
lm = LoginManager()

def create_app():
  app = Flask(__name__)
  app.config.from_object('config')
  app.config["CACHE_TYPE"] = "null"
  db.init_app(app)
  db.app = app
  lm.init_app(app)
  lm.app = app
  lm.login_view = 'main.login'

  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)
  from .auth import auth as auth_blueprint
  app.register_blueprint(auth_blueprint)
  from .events import events as events_blueprint
  app.register_blueprint(events_blueprint)

  return app

