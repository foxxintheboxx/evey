from flask import redirect, url_for, session, request, render_template
from flask_oauth import OAuth
from app import app
import requests
import json
import traceback

SECRET_KEY = 'development key'
TOKEN = "EAAYbvNuO44cBAGcjOnLfqTR0RtMVUVvZBZAIkFaEGNifKqC6kIPPDuYdwDdKaS7c9I12gGohd0NPFmoIGF9ikZCmHBZCYi7Tq1SKDwMs6sRBUofqGTSdyhFLB949kZBVHaW9h6ZCezKaRY4IPxvALDLGvCJDjzxMoZD"
WEBHOOK = "518aaf94cff67b8498a4a811b91a50be40c75de1398f52b066"
FACEBOOK_APP_ID = '1719347811640199'
FACEBOOK_APP_SECRET = '04d030e82620967b0109f9fec8a36592'


app.secret_key = SECRET_KEY
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'read_custom_friendlists' }
)


@app.route('/' + WEBHOOK, methods=['GET', 'POST'])
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
            payload = {'recipient': {'id': sender}, 'message': {'text': "Hello World"}}
            user_details_url = "https://graph.facebook.com/v2.6/%s"%sender
            user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':TOKEN}
            r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + TOKEN, json=payload) # Lets send it
            r = requests.get(user_details_url, user_details_params).json()
            print(r)
    except Exception as e:
      print traceback.format_exc() # something went wrong
  elif request.method == 'GET': # For the initial verification
    if request.args.get('hub.verify_token') == 'eveytesting':
      return request.args.get('hub.challenge')
    return "Wrong Verift Token"
  return "Hello World"


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
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
    print(facebook.get("/me/friends").data)
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')