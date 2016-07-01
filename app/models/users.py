
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .calendars import Calendar

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


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    fb_uid = db.Column(db.String(64), index=True, unique=True)
    messenger_uid = db.Column(db.String(64), index=True, unique=True)
    date_created = db.Column(db.DateTime, index=True)
    last_date_used = db.Column(db.DateTime, index=True)

    did_onboarding = db.Column(db.Integer, index=True)
    is_editing_location = db.Column(db.String, index=True)
    is_adding_time = db.Column(db.String, index=True)
    is_setting_time = db.Column(db.String, index=True)
    is_removing_time = db.Column(db.String, index=True)
    is_adding_event_name = db.Column(db.Integer, index=True)

    first_name = db.Column(db.String(65), index=True)
    last_name = db.Column(db.String(64), index=True)
    timezone = db.Column(db.Integer, index=True)

    last_msg = db.Column(db.String)
    date_conv_session = db.Column(db.Integer, index=True)
    location_conv_session = db.Column(db.Integer, index=True)
    calendar = db.relationship("Calendar",
                               uselist=False,
                               back_populates='user')
    location_polls = db.relationship('Locationpoll',
                                     secondary=locationpoll_user_association,
                                     backref=db.backref('users'))
    date_polls = db.relationship('Datepoll',
                                 secondary=datepoll_user_association,
                                 backref=db.backref('users'))
    created_events = db.relationship('Event',
                                     backref='creator',
                                     lazy='dynamic')

    def __init__(self, messenger_uid):
        self.date_created = datetime.utcnow()
        self.messenger_uid = messenger_uid
        self.date_conv_session = 0
        self.did_onboarding = 0
        self.is_editing_location = ""
        self.is_adding_time = ""
        self.is_removing_time = ""
        self.is_setting_time = ""
        self.location_conv_session = 0
        print("uhh wtf")
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
