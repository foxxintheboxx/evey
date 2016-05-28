from flask import redirect, url_for, flash, session, request, render_template, g
from . import main
from .convengine import EveyEngine
from config import SECRET_KEY, TOKEN, WEBHOOK, WEBHOOK_TOKEN
from ..utils import FB_GRAPH_URL, MESNGR_API_URL
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

def fetch_user_data(user_url, params):
  return requests.get(user_url, params=params).json()


def post_response_msgs(msgs, sender):
  for msg in msgs:
    payload = {'recipient': {'id': sender}, 'message': msg}
    r = requests.post(MESNGR_API_URL + TOKEN, json=payload)


@main.route('/' + WEBHOOK, methods=['GET', 'POST'])
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

      if len(postbacks):
        user = usr_manager.handle_messenger_user(user_data)
        evey = EveyEngine(user_data["first_name"], user)
        resp_msgs = evey.handle_postback(postbacks)
        post_response_msgs(resp_msgs, sender)

      if len(msgs):
        user = usr_manager.handle_messenger_user(user_data)
        evey = EveyEngine(user_data["first_name"], user)
        print("msgs: %s" % str(msgs))
        resp_msgs = evey.understand(msgs)
        post_response_msgs(resp_msgs, sender)
    except Exception as e:
      print traceback.format_exc() # something went wrong
  elif request.method == 'GET': # For the initial verification
    if request.args.get('hub.verify_token') == WEBHOOK_TOKEN:
      return request.args.get('hub.challenge')
    return 'Wrong Verify Token'
  return "hello world"

@lm.user_loader
def load_user(id):
  return User.query.get(int(id))

@main.route('/authorize/facebook')
def oauth_authorize():
  if not current_user.is_anonymous:
    return redirect(url_for('index'))
  oauth = OAuthSignIn.get_provider('facebook')
  return oauth.authorize()

@main.route('/callback/facebook')
def oauth_callback():
  if not current_user.is_anonymous:
    return redirect(url_for('index'))
  oauth = OAuthSignIn.get_provider("facebook")
  user_data = oauth.callback()
  if user_data.get("fb_uid") is None:
    return "access Denied"
  user = usr_manager.handle_fb_user(user_data)
  if user != None:
    messenger_uid = user.messenger_uid
    resp_msg = EveyEngine(user.first_name, user).understand(["site visit"])
    for msg in resp_msg:
      payload = {'recipient': {'id': messenger_uid}, 'message':msg}
      r = requests.post(MESNGR_API_URL + TOKEN, json=payload)
  return render_template("index.html")


@main.route('/')
@login_required
def index():
    return render_template("index.html")

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

@main.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user, remember = True)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))


