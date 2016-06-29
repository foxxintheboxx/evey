
from .. import db

calendar_event_association = db.Table(
    'calendar_event_association', db.Model.metadata,
    db.Column('calendar_id', db.Integer, db.ForeignKey('calendar.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
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
        return '<Calendar of %r>' % self.user.name
