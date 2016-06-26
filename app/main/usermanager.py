
from time import mktime
import time
from datetime import datetime

from .. import db
from ..models import User
from ..utils import save

class UserManager():

  def handle_messenger_user(self, user_data):
    return self.evey_user_exists(user_data)

  def handle_website_user(self, user_data):
    return self.evey_user_exists(user_data)

  def evey_user_exists(self, user_data):
    uid = user_data.get("messenger_uid")
    user = db.session.query(User).filter((User.messenger_uid==uid)).first()
    print(user_data)
    if user == None:
        user = User(messenger_uid=uid)
        user.name = user_data.get("first_name") + " " + user_data.get("last_name")
        save([user])
    return user

