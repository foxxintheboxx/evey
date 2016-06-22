
from time import mktime
import time
from datetime import datetime

from .. import db
from ..models import User, MessengerUser, FBUser

class UserManager():


  def handle_messenger_user(self, user_data):
    return self.evey_user_exists(user_data)

  def handle_website_user(self, user_data):
    return self.evey_user_exists(user_data)

  def evey_user_exists(self, user_data):
    uid = user_data.get("messenger_uid")
    user = db.session.query(User).filter((User.messenger_uid==uid)).first()
    return user

