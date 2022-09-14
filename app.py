from flask import Flask
from config import DefCon
from models import *
from flask_sqlalchemy import SQLAlchemy

app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(DefCon)
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

from controllers import *

if __name__ == '__main__':
  app.run(debug=True)
