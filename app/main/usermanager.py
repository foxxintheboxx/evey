
from time import mktime
import time
from datetime import datetime

from .. import db
from ..models.users import User
from ..utils import save, fetch_user_data

class UserManager():

  def handle_messenger_user(self, user_data):
    return self.evey_user_exists(user_data)

  def handle_website_user(self, user_data):
    return self.evey_user_exists(user_data)

  def evey_user_exists(self, muid):
    user = db.session.query(User).filter((User.messenger_uid==muid)).first()
    if user == None:
        user_data = fetch_user_data(muid)

        print(user_data)
        user = User(messenger_uid=muid)
        user.name = user_data.get("first_name") + " " + user_data.get("last_name")
        user.first_name = user_data.get("first_name")
        save([user])
    return user

