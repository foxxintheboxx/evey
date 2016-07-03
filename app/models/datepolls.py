
from .. import db
from ..utils import format_dateobj, number_to_emojistr
import const as c
from datetime import timedelta

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

    def format_poll(self, offset=0, use_day=True, use_at=True, indent="",
                    use_emoji_number=True, use_votes=True):
        text = format_dateobj(self.datetime, self.end_datetime, offset,
                              use_day=use_day, use_at=use_at)
        text = "%s%s %s" % (indent, number_to_emojistr(self.poll_number),
                            text)
        if (use_votes):
          votes_str = ""
          if self.votes() > 2:
              votes = "%sx%s" % (self.votes(), c.GUY_EMOJI)
          else:
              votes = c.GUY_EMOJI * self.votes()
          text += ", %s" % votes
        return text
