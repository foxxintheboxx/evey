from flask import redirect, url_for, session, request, render_template
from flask_oauth import OAuth
from . import main
from config import SECRET_KEY, TOKEN, WEBHOOK, WEBHOOK_TOKEN
from ..utils import FB_GRAPH_URL, MESNGR_API_URL
import requests
import json
import traceback

from ..models import User, Conversation, Message, MessengerUser
from .. import db
from usermanager import UserManager


main.secret_key = SECRET_KEY
oauth = OAuth()
FACEBOOK_APP_ID = '1719347811640199'
FACEBOOK_APP_SECRET = '04d030e82620967b0109f9fec8a36592'
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='1719347811640199',
    consumer_secret='04d030e82620967b0109f9fec8a36592',
    request_token_params={'scope': 'public_profile' }
)
usr_manager = UserManager()

SIGNUP = 'Hey %s, signing up with facebook helps me connect you with your friends. Plz sign in https://eveyai.herokuapp.com'
WAIT = 'OK %s, Thanks for registering. I\'m not totally developed yet -- Stay Tuned'
@main.route('/' + WEBHOOK, methods=['GET', 'POST'])
def webhook():
  if request.method == 'POST':
    try:
      data = json.loads(request.data)
      for entry in data['entry']:
        for message in entry['messaging']:
          if 'message' in message:

            sender = message['sender']['id'] # Sender ID
            user_details_url = FB_GRAPH_URL + sender
            user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':TOKEN}
            user_data = requests.get(user_details_url, user_details_params).json()
            user_data['messenger_uid'] = sender
            user = usr_manager.handle_messenger_user(user_data)
            text = message['message']['text'] # Incoming Message Text
            resp_text = WAIT % user_data['first_name']
            if user == None:
              resp_text = SIGNUP % user_data['first_name']
            payload = {'recipient': {'id': sender}, 'message': {'text': resp_text}}
            r = requests.post(MESNGR_API_URL + TOKEN, json=payload) # Lets send it
    except Exception as e:
      print traceback.format_exc() # something went wrong
  elif request.method == 'GET': # For the initial verification
    if request.args.get('hub.verify_token') == WEBHOOK_TOKEN:
      return request.args.get('hub.challenge')
    return 'Wrong Verift Token'
  return 'Hello World'


@main.route('/')
def index():
    return redirect(url_for('main.login'))


@main.route('/login')
def login():
    return facebook.authorize(callback=url_for('main.facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@main.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
      return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description'])
    session['oauth_token'] = (resp['access_token'], '')
    print(resp)
    me = facebook.get('/me')
    print(facebook.get('/me/friends').data)
    user_details_url = 'https://graph.facebook.com/v2.6/%s'%me.data['id']
    user_details_params = {'fields':'picture', 'access_token':resp['access_token']}

    r = requests.get(user_details_url, user_details_params).json()

    me.data['profile_pic'] = r['profile_pic']
    me.data['fb_uid'] = me.data['id']
    me.data['first_name'] = me.data['name'].split()[0]
    me.data['last_name'] = me.data['name'].split()[1]
    user = usr_manager.handle_fb_user(me.data)
    if user != None:
      messenger_uid = user.messenger_uid
      resp_text = WAIT % me.data['first_name']
      payload = {'recepient': {'id': messenger_uid}, 'message': {'text': resp_text}}
      requests.post(MESNGR_API_URL + TOKEN, json=payload)
    print(r)
    #return 'Logged in as id=%s name=%s redirect=%s' % \
    #    (me.data['id'], me.data['name'], request.args.get('next'))
    return render_template('index.html')

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')
