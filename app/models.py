
from . import db
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .utils import save, delete

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
  is_editing_location = db.Column(db.String, index=True)
  is_adding_time = db.Column(db.String, index=True)
  is_setting_time = db.Column(db.String, index=True)
  is_removing_time = db.Column(db.String, index=True)
  first_name = db.Column(db.String(64), index=True)
  last_name = db.Column(db.String(64), index=True)
  last_msg = db.Column(db.String)
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
    self.is_editing_location = ""
    self.is_adding_time = ""
    self.is_removing_time = ""
    self.is_setting_time = ""
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
  message_uid = db.Column(db.String)
  time = db.Column(db.String)

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

  def user_added_time(self, user):
    for p in self.date_polls:
      for u in p.users:
        if u.messenger_uid == user.messenger_uid:
          return True
    return False

  def append_datepoll(self, poll):
    self.date_polls.append(poll)
    poll.poll_number = len(self.date_polls.all())

  def attendees(self):
    return [cal.user for cal in self.calendars]

  def sort_datepolls(self):
    datepoll_list = self.get_datepolls()
    for i in range(len(datepoll_list)):
      datepoll_list[i].poll_number = i + 1

  def get_datepolls(self):
    datepoll_list = self.date_polls.all()
    datepoll_list.sort(key=lambda x: x.votes(), reverse=True)
    return datepoll_list

  def add_new_interval(self, to_dateobj, from_dateobj, user):
    date_polls = self.get_datepolls()
    intersecting_polls = []
    old_polls = []
    for poll in date_polls:
      if poll.end_datetime == None and from_dateobj != None:
        continue # TODO
      print("to " + str(to_dateobj))
      print("db " + str(poll.datetime))
      print("from " + str(from_dateobj))
      print("db end" + str(poll.end_datetime))
      time0 = min(to_dateobj, poll.datetime)
      time1 = max(to_dateobj, poll.datetime)
      time2 = min(poll.end_datetime, from_dateobj)
      time3 = max(poll.end_datetime, from_dateobj)
      if (time0 == time1 and time2 == time3):
        poll.users.append(user)
        return [poll]
      elif (time0 == time1 and time2 < time3): # 1
        inner_interval = Datepoll()
        outer_interval = Datepoll()
        inner_interval.datetime = time0
        inner_interval.end_datetime = time2
        outer_interval.datetime = time2
        outer_interval.end_datetime = time3
        users = poll.users
        if (time2 == from_dateobj):
          outer_interval.add_users(users)
          users.append(user)
          inner_interval.add_users(users)
        else:
          outer_interval.add_users([user])
          inner_interval.add_users(users)
        intersecting_polls.extend([inner_interval, outer_interval])
        old_polls.append(poll)
#      elif (time0 < time1 and time2 == time3):
#        if (time1 =
#     elif (poll.datetime <= from_dateobj and from_dateobj <= poll.end_datetime):
    if len(intersecting_polls) == 0:
      poll = Datepoll()
      poll.datetime = to_dateobj
      poll.end_datetime = from_dateobj
      poll.add_users([user])
      intersecting_polls.append(poll)
    for poll in intersecting_polls:
      self.append_datepoll(poll)
    delete(old_polls)
    save(intersecting_polls)




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
  datetime = db.Column(db.DateTime(timezone=True))
  end_datetime = db.Column(db.DateTime(timezone=True))
  poll_number = db.Column(db.Integer)  # to use when choosing

  def votes(self):
    return len(self.users)

  def add_users(self, users_):
    for user in users_:
      self.users.append(user)

