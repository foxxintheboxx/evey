from flask import redirect, url_for, session, request, render_template
from flask_oauth import OAuth
from . import main
from config import SECRET_KEY, TOKEN, WEBHOOK, WEBHOOK_TOKEN
import requests
import json
import traceback

from ..models import User, Conversation, Message, MessengerUser
from .. import db
from onboarding_utils import extract_pic_uid


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


@main.route('/' + WEBHOOK, methods=['GET', 'POST'])
def webhook():
  if request.method == 'POST':
    try:
      data = json.loads(request.data)
      print(data)
      for entry in data['entry']:
        for message in entry['messaging']:
          if 'message' in message:
            text = message['message']['text'] # Incoming Message Text
            print(text)
            sender = message['sender']['id'] # Sender ID
            payload = {'recipient': {'id': sender}, 'message': {'text': "Hey, signing up with facebook \
                                                                        helps me connect you with your friends. \
                                                                        Plz sign in https://eveyai.herokuapp.com"}}
            user_details_url = "https://graph.facebook.com/v2.6/%s"%sender
            user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':TOKEN}

            user_data = requests.get(user_details_url, user_details_params).json()
            extracted_id = extract_pic_uid(user_data['profile_pic'])

            messenger_user = MessengerUser(messenger_uid=int(sender),
                                           first_name=user_data['first_name'],
                                           last_name=user_data['last_name'],
                                           profile_pic_id=extracted_id)
            db.session.add(messenger_user)
            db.session.commit()



            print(r)
            r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + TOKEN, json=payload) # Lets send it
    except Exception as e:
      print traceback.format_exc() # something went wrong
  elif request.method == 'GET': # For the initial verification
    if request.args.get('hub.verify_token') == WEBHOOK_TOKEN:
      return request.args.get('hub.challenge')
    return "Wrong Verift Token"
  return "Hello World"


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
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    print(resp)
    me = facebook.get('/me')
    print("/" + me.data['id'] + "/" + "friends")
   # print(facebook.get("/" + me.data['id'] + "/" + "friendlists").data)
    #print(facebook.get("/me/friends").data)
    user_details_url = "https://graph.facebook.com/v2.6/%s"%me.data['id']
    user_details_params = {'fields':'picture', 'access_token':resp['access_token']}
    r = requests.get(user_details_url, user_details_params).json()
    print(r)
    #print(json.dumps(facebook.get('/me/picture').data))
    #return 'Logged in as id=%s name=%s redirect=%s' % \
    #    (me.data['id'], me.data['name'], request.args.get('next'))
    return render_template("index.html")

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')
