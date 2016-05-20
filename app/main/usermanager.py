
from .. import db
from models import User, MessengerUser, FBUser

class UserManager():

  def __init__(self):
    self.response = {"fb_user":False,"messenger_user":False,
                     "evey_user":False}

  def handle_messenger_user(self, user_data):
    users = MessengerUser.query.filter(messenger_uid=user_data["messenger_uid"])
    if len(users) == 1:
      user = self.evey_user_exists(user_data)
      if user != None:
        self.set_all_users(True)
        return user
    else:
      profile_pic_id = self.extract_pic_uid(user_data["profile_pic"])
      m_user = MessengerUser(messenger_uid=user_data["fb_uid"],
                              first_name=user_data["first_name"],
                              last_name=user_data["last_name"],
                              profile_pic_id=profile_pic_id)
      db.session.add(u)
      db.session.commit()
      uids = self.duo_accounts_exists(user_data)
      if uids != None:
        user = self.create_evey_user(user_data, uids)
        self.set_all_users(True)
        return user
    self.response["messenger_user"] = True
    return None

  def handle_fb_user(self, user_data):
    users = FBUser.query.filter(fb_uid=user_data["fb_uid"])
    if len(users) == 1:
      user = self.evey_user_exists(user_data)
      if user != None:
        self.set_all_users(True)
        return user
    else:
      profile_pic_id = self.extract_pic_uid(user_data["profile_pic"])
      fb_user = FBUser(fb_uid=user_data["fb_uid"],
                       first_name=user_data["first_name"],
                       last_name=user_data["last_name"],
                       profile_pic_id=profile_pic_id)
      db.session.add(u)
      db.session.commit()
      uids = self.duo_accounts_exists(user_data)
      if uids != None:
        user = self.create_evey_user(user_data, uids)
        self.set_all_users(True)
        return user
    self.response["fb_user"] = True
    return None

  def set_all_users(self, boolean):
    self.response["messenger_user"] = boolean
    self.response["fb_user"] = boolean
    self.response["evey_user"] = boolean

  def evey_user_exists(self, user_data):
    uid = user_data.get("messenger_uid") or user_data.get("fb_uid")
    users = db.session.query(User) \
          .filter((User.messenger_uid==uid) | (User.fb_uid==uid))
    if len(users) == 1:
      return users[0]
    return None

  def duo_accounts_exists(self, user_data):
    pic_uid = self.extract_pic_uid(user_data['profile_pic'])
    messenger_users = MessengerUser.query.filter(profile_pic_id=pic_uid)
    fb_users = FBUser.query.filter(profile_pic_id=pic_uid)
    if len(messenger_users) == 1 and len(fb_users) == 1:
      return {"messenger_uid": messenger_users[0].messenger_uid,
              "fb_uid": fb_users[0].fb_uid}
    return None

  def create_evey_user(self, user_data, uids):
    name = user_data["first_name"] + " " + user_data["last_name"]
    user = User(name=name, first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                fb_uid=uids["fb_uid"],
                messenger_uid=uids["messenger_uid"])
    db.session.add(user)
    db.session.commit()
    return user

  def extract_pic_uid(self, pic_url):
    prefix = pic_url[:pic_url.index('jpg') - 1]
    return prefix[prefix.rfind('/') + 1]

usr_manager = UserManager()
