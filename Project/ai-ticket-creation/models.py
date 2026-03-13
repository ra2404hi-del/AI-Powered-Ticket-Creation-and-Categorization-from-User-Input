from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(120), unique=True) 
    password = db.Column(db.String(200))
    role = db.Column(db.String(50), default="User")


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(100))        # ✅ NEW
    priority = db.Column(db.String(20))         # ✅ NEW

    status = db.Column(db.String(20), default="Open")

    date_created = db.Column(db.DateTime, default=datetime.now)   # updated
    updated_at = db.Column(db.DateTime, default=datetime.now)     # ✅ NEW