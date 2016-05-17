from app import db

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  profile_pic_id = db.Column(db.String(64), index=True, unique=True)
  name = db.Column(db.String(120), index=True, unique=True)
  first_name = db.Column(db.String(64), index=True, unique=True)
  last_name = db.Column(db.String(64), index=True, unique=True)

  def __repr__(self):
      return '<User %r>' % (self.name)
