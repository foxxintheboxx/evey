
from . import db
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

Base = declarative_base()

calendar_event_association = db.Table(
    'calendar_event_association', db.Model.metadata,
    db.Column('calendar_id', db.Integer, db.ForeignKey('calendar.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
    )

locationpoll_user_association = db.Table(
    'locationpoll_user_association', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('locationpoll_id', db.Integer, db.ForeignKey('locationpoll.id')),
    )

datepoll_user_association = db.Table(
    'datepoll_user_association', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('datepoll_id', db.Integer, db.ForeignKey('datepoll.id')),
    )


class MessengerUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  messenger_uid = db.Column(db.String(64), index=True, unique=True)
  first_name = db.Column(db.String(64), index=True)
  last_name = db.Column(db.String(64), index=True)
  profile_pic_id = db.Column(db.String(120), index=True, unique=True)

  def __repr__(self):
    return '<MessengerUser %r>' % (self.first_name + " " + self.last_name)

class FBUser(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fb_uid = db.Column(db.String(64), index=True, unique=True)
  first_name = db.Column(db.String(64), index=True)
  last_name = db.Column(db.String(64), index=True)
  profile_pic_id = db.Column(db.String(120), index=True, unique=True)

  def __repr__(self):
    return '<FBUser %r>' % (self.first_name + " " + self.last_name)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), index=True)
  fb_uid = db.Column(db.String(64), index=True, unique=True)
  messenger_uid = db.Column(db.String(64), index=True, unique=True)
  username = db.Column(db.String(20), unique=True , index=True)
  password_hash = db.Column(db.String(128), index=True)
  date_created = db.Column(db.DateTime, index=True)
  did_onboarding = db.Column(db.Integer, index=True)

  first_name = db.Column(db.String(64), index=True)
  last_name = db.Column(db.String(64), index=True)
  conversations = db.relationship('Conversation',
                                   backref='user',
                                   lazy='dynamic')
  date_conv_session = db.Column(db.Integer, index=True)
  location_conv_session = db.Column(db.Integer, index=True)

  messages = db.relationship('Message',
                              backref='user',
                              lazy='dynamic')
  calendar = db.relationship("Calendar",
                             uselist=False,
                             back_populates="user")
  location_polls = db.relationship('Locationpoll',
                                   secondary=locationpoll_user_association,
                                   backref=db.backref('users'))
  date_polls = db.relationship('Datepoll',
                               secondary=datepoll_user_association,
                               backref=db.backref('users'))


  def __init__(self, username, password, messenger_uid):
    self.username = username
    self.password = password
    self.registered_on = datetime.utcnow()
    self.messenger_uid = messenger_uid
    self.date_conv_session = 0
    self.did_onboarding = 0
    self.location_conv_session = 0
    self.calendar = Calendar()

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return unicode(self.id)

  @property
  def password(self):
      raise AttributeError('password is not a readable attribute')

  @password.setter
  def password(self, password):
      self.password_hash = generate_password_hash(password)

  def verify_password(self, password):
      return check_password_hash(self.password_hash, password)

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

class Calendar(db.Model):
  __tablename__ = 'calendar'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  user = db.relationship("User", back_populates="calendar")

  events = db.relationship('Event',
                secondary=calendar_event_association,
                backref=db.backref('calendars'))
  def __repr__(self):
    return '<Calendar of %r>' % self.user.name



class Event(db.Model):
  __tablename__ = 'event'
  id = db.Column(db.Integer, primary_key=True)
  event_hash = db.Column(db.String, unique=True)
  calendar_id = db.Column(db.Integer, db.ForeignKey('calendar.id'))
  datetime = db.Column(db.DateTime)
  duration = db.Column(db.Integer)
  title = db.Column(db.String(64))

  location_polls = db.relationship('Locationpoll',
                                   backref='event',
                                   lazy='dynamic')
  date_polls = db.relationship('Datepoll',
                               backref='event',
                               lazy='dynamic')


  def __repr__(self):
    return '<Event %r>' % self.title

  def get_top_poll(self, poll):
    votes = -1
    top_p = None
    for p in poll:
      if p.votes() > votes:
        top_p = p
        votes = p.votes()
    return top_p

  def get_top_date(self):
    return self.get_top_poll(self.date_polls)

  def get_top_local(self):
    return self.get_top_poll(self.location_polls)

  def attendees(self):
    return [cal.user for cal in self.calendars]

class Locationpoll(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
  poll_type = db.Column(db.String)
  name = db.Column(db.String)

  def votes(self):
    return len(self.users)

class Datepoll(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
  poll_type = db.Column(db.String)
  datetime = db.Column(db.DateTime)

  def votes(self):
    return len(self.users)

