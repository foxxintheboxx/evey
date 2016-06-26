
from time import mktime
import time
from datetime import datetime

from .. import db
from ..models import User, MessengerUser, FBUser
from ..utils import save

class UserManager():

  def handle_messenger_user(self, user_data):
    return self.evey_user_exists(user_data)

  def handle_website_user(self, user_data):
    return self.evey_user_exists(user_data)

  def evey_user_exists(self, user_data):
    uid = user_data.get("messenger_uid")
    user = db.session.query(User).filter((User.messenger_uid==uid)).first()
    if user == None:
        user = User()
        user.messenger_uid = user_data.get("messenger_uid")
        save(user)
    return user

