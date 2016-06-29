
from .. import db

class Locationpoll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    poll_type = db.Column(db.String)
    name = db.Column(db.String)

    def votes(self):
        return len(self.users)