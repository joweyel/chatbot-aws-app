# pylint: disable=E1102, R0903: too-few-public-methods

from sqlalchemy.sql import func
from . import db


class Chat(db.Model):
    """Chat schema to store messages."""
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    messages = db.relationship("Message", backref="chat", lazy=True)


class Message(db.Model):
    """Message schema to store messages in a chat."""
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"))
