from flask_sqlalchemy import SQLAlchemy
from app import app
db = SQLAlchemy(app)

#for user database
class User(db.Model):
    __tablename__ = 'User_Credentials'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String,  nullable=False)
    fname = db.Column(db.String,  nullable=False)

#for tracker databse
class Tracker(db.Model):
    __tablename__ = 'Tracker'
    t_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    u_id = db.Column(db.Integer, db.ForeignKey("User_Credentials.user_id"), nullable=False)
    t_name = db.Column(db.String,  nullable=False)
    desc = db.Column(db.String,  nullable=False)
    t_type = db.Column(db.String,  nullable=False)

#for linker database
class Linker(db.Model):
    __tablename__ = 'Linker'
    l_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False, unique=True)
    tl_id = db.Column(db.Integer, db.ForeignKey("Tracker.t_id"), nullable=False)
    t_value = db.Column(db.Integer,  nullable=False)
    comm = db.Column(db.String,  nullable=True)
    timest = db.Column(db.DateTime,  nullable=False)
    timedr = db.Column(db.String, nullable=False)