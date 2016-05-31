from flask import redirect, url_for, flash, session, request, render_template, g
from . import main
from ..convengine import EveyEngine
from config import SECRET_KEY, TOKEN, WEBHOOK, WEBHOOK_TOKEN
from ..utils import FB_GRAPH_URL, MESNGR_API_URL, fetch_user_data
import requests
import json
import traceback

from ..models import User, Conversation, Message, MessengerUser
from .. import db, lm
from usermanager import UserManager
from flask.ext.login import UserMixin, login_user, logout_user, current_user, \
                            login_required
from ..oauth import OAuthSignIn


main.secret_key = SECRET_KEY
usr_manager = UserManager()


def post_response_msgs(msgs, sender):
  for msg in msgs:
    payload = {'recipient': {'id': sender}, 'message': msg}
    r = requests.post(MESNGR_API_URL + TOKEN, json=payload)


@main.route('/' + WEBHOOK, methods=['GET'])
def verification():
  if request.args.get('hub.verify_token') == WEBHOOK_TOKEN:
    return request.args.get('hub.challenge')
  return 'Wrong Verify Token'

@main.route('/' + WEBHOOK, methods=['POST'])
def webhook():
  if request.method == 'POST':
    try:
      data = json.loads(request.data)
      print(data)
      for entry in data['entry']:
        sender = ""
        msgs = []
        postbacks = []
        for message in entry['messaging']:
          if sender == "":
            sender = message['sender']['id'] # Sender ID
          if 'message' in message:
            print("messsage")
            msgs.append(message['message']['text'])
          if 'postback' in message:
            print("postback")
            postbacks.append(message['postback']['payload'])

      user_details_params = {'fields':'first_name,last_name,profile_pic',
                                      'access_token':TOKEN}
      user_data = fetch_user_data(FB_GRAPH_URL + sender,
                                  user_details_params)
      user_data['messenger_uid'] = sender
      user = usr_manager.handle_messenger_user(user_data)
      evey = EveyEngine(user_data["first_name"], user, sender)
      if user is None:
        resp_msgs = evey.understand(["signup"])
        post_response_msgs(resp_msgs, sender)
      elif len(postbacks):
        resp_msgs = evey.handle_postback(postbacks)
        post_response_msgs(resp_msgs, sender)
      elif len(msgs):
        print("msgs: %s" % str(msgs))
        resp_msgs = evey.understand(msgs)
        post_response_msgs(resp_msgs, sender)
    except Exception as e:
      print traceback.format_exc() # something went wrong
  return "hello world"

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))


@main.route('/')
@login_required
def index():
    if current_user != None:
      print(current_user)
      messenger_uid = current_user.messenger_uid

      resp_msg = EveyEngine(current_user.first_name, current_user,
                            messenger_uid).understand(["site visit"])
      for msg in resp_msg:
        payload = {'recipient': {'id': messenger_uid}, 'message':msg}
        r = requests.post(MESNGR_API_URL + TOKEN, json=payload)
    return render_template("index.html")

