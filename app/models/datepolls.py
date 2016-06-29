
from .. import db

class Datepoll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    poll_type = db.Column(db.String)
    datetime = db.Column(db.DateTime(timezone=True))
    end_datetime = db.Column(db.DateTime(timezone=True))
    poll_number = db.Column(db.Integer)  # to use when choosing

    def __init__(self, datetime=None, end_datetime=None):
        self.datetime = datetime
        self.end_datetime = end_datetime

    def votes(self):
        return len(self.users)

    def add_users(self, users_):
        for user in users_:
            self.users.append(user)
