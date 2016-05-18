from app import db

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  profile_pic_id = db.Column(db.String(64), index=True, unique=True)
  name = db.Column(db.String(120), index=True, unique=True)
  synced_fb = db.Column(db.Integer, index=True, unique=True)
  first_name = db.Column(db.String(64), index=True, unique=True)
  last_name = db.Column(db.String(64), index=True, unique=True)
  stared_conversations = db.relationship('Conversations',
                                         backref='sender',
                                         lazy='dynamic')
  received_conversations = db.relationship('Conversations',
                                           backref='recepient',
                                           lazy='dynamic')

  def __repr__(self):
      return '<User %r>' % (self.name)

class Conversation(db.Model):
  id = Column(Integer, primary_key=True)
  recepient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  messages = db.relationships('Messages',
                              backref='conversation',
                              lazy='dynamic')

  def __repr__(self):
      return '<Conversation between sender: %r recepient: %r>' % (self.sender.name,
                                                                  self.recepient.name)

class Message(db.Model):
  id = Column(Integer, primary_key=True)
  body = db.Column(db.String(140))
  conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))

  def __repr__(self):
      return '<Message %r>' % self.body
