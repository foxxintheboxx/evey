
from . import db

class MessengerUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  messenger_uid = db.Column(db.Integer, index=True, unique=True)
  first_name = db.Column(db.String(64), index=True, unique=True)
  last_name = db.Column(db.String(64), index=True, unique=True)
  profile_pic_id = db.Column(db.String(64), index=True, unique=True)

class FBUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fb_uid = db.Column(db.Integer, index=True, unique=True)
  first_name = db.Column(db.String(64), index=True, unique=True)
  last_name = db.Column(db.String(64), index=True, unique=True)
  profile_pic_id = db.Column(db.String(64), index=True, unique=True)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), index=True, unique=True)
  messenger_uid = db.Column(db.Integer, index=True, unique=True)
  fb_uid = db.Column(db.Integer, index=True, unique=True)
  first_name = db.Column(db.String(64), index=True, unique=True)
  last_name = db.Column(db.String(64), index=True, unique=True)
  conversations = db.relationship('Conversation',
                                   backref='user',
                                   lazy='dynamic')
  messages = db.relationship('Message',
                              backref='author',
                              lazy='dynamic')


  def __repr__(self):
      return '<User %r>' % (self.name)

class Conversation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  messages = db.relationship('Message',
                              backref='conversation',
                              lazy='dynamic')

  def __repr__(self):
      return '<Conversation between sender: %r recepient: %r>' % (self.sender.name,
                                                                  self.recepient.name)

class Message(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  body = db.Column(db.String(140))
  conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))

  def __repr__(self):
      return '<Message %r>' % self.body

