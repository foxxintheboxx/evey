
from . import db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MessengerUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  messenger_uid = db.Column(db.String(64), index=True, unique=True)
  first_name = db.Column(db.String(64), index=True)
  last_name = db.Column(db.String(64), index=True)
  profile_pic_id = db.Column(db.String(120), index=True, unique=True)

  def __repr__(self):
    return '<MessengerUser %r>' % self.first_name + " " + self.last_name

class FBUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fb_uid = db.Column(db.String(64), index=True, unique=True)
  first_name = db.Column(db.String(64), index=True)
  last_name = db.Column(db.String(64), index=True)
  profile_pic_id = db.Column(db.String(120), index=True, unique=True)

  def __repr__(self):
    return '<FBUser %r>' % self.first_name + " " + self.last_name

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), index=True, unique=True)
  fb_uid = db.Column(db.String(64), index=True, unique=True)
  messenger_uid = db.Column(db.String(64), index=True, unique=True)


  first_name = db.Column(db.String(64), index=True, unique=True)
  last_name = db.Column(db.String(64), index=True, unique=True)
  conversations = db.relationship('Conversation',
                                   backref='user',
                                   lazy='dynamic')
  messages = db.relationship('Message',
                              backref='user',
                              lazy='dynamic')
  calendar = db.relationship("Calendar",
                             uselist=False,
                             back_populates="user")



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
  body = db.Column(db.Text())
  conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))

  def __repr__(self):
      return '<Message from %r>' % self.user.name


### Calendar Models

calendar_event_association = db.Table(
    'calendar_event_association', db.Model.metadata,
    db.Column('calendar_id', db.Integer, db.ForeignKey('calendar.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    schema='main'
    )

class Calendar(db.Model):
  __tablename__ = 'calendar'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  user = db.relationship("User", back_populates="calendar")

  events = db.relationship('Event',
                secondary=calendar_event_association,
                backref=db.backref('calendars'))
  def __repr__(self):
    return '<Calendar of %r>' % user.name

class Event(db.Model):
  __tablename__ = 'event'
  id = db.Column(db.Integer, primary_key=True)
  calendar_id = db.Column(db.Integer, db.ForeignKey('calendar.id'))
  datetime = db.Column(db.Date)
  duration = db.Column(db.Integer)
  title = db.Column(db.String(64))

  def __repr__(self):
    return '<Event %r>' % self.title

