from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()
def create_app():
  app = Flask(__name__)
  app.config.from_object('config')
  db.init_app(app)
  db.app = app
  from .main import main as main_blueprint
  app.register_blueprint(main_blueprint)

  return app

