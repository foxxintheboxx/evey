from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
from config import OAUTH_CREDENTIALS


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = OAUTH_CREDENTIALS[provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        print("hello")
        return url_for('main.oauth_callback', _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        print('authorize')
        auth_url = (self.service.get_authorize_url(
                    scope='public_profile',
                    response_type='code',
                    redirect_uri=self.get_callback_url())
        )
        print(auth_url)
        return redirect(auth_url)

    def callback(self):
        if 'code' not in request.args:
            return {}
        print('callback')
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me?fields=id,name,picture').json()
        print(me)
        return {
            'fb_uid': me['id'],
            'first_name': me['name'].split()[0],
            'last_name': me['name'].split()[1],
            'profile_pic':me['picture']['data']['url']
        }


