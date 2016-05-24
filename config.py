import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db'))
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'development key'
# messenger access toke
TOKEN = "EAAYbvNuO44cBAGcjOnLfqTR0RtMVUVvZBZAIkFaEGNifKqC6kIPPDuYdwDdKaS7c9I12gGohd0NPFmoIGF9ikZCmHBZCYi7Tq1SKDwMs6sRBUofqGTSdyhFLB949kZBVHaW9h6ZCezKaRY4IPxvALDLGvCJDjzxMoZD"

WEBHOOK = "18aaf94cff67b8498a4a811b91a50be40c75de1398f52b066"
WEBHOOK_TOKEN = 'eveytesting'
FACEBOOK_APP_ID = '1719347811640199'

FACEBOOK_APP_SECRET = 'd5163109796d51e5d875ac56797c11c6'


# witai
WIT_API = "https://api.wit.ai/"
WIT_APP_ID = "572dd95b-bc3f-4a0c-9276-2cf32b282119"
WIT_SERVER = "7RT2JNPPHTNBU6X3HNMUSIMGODL6SWW4"


#IMG_ENDPOINTS
EXAMPLE_0 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/ee143.png?token=AE7-ygerebQgUGAXPpeiu-zEqUp0Kcs6ks5XS9lUwA%3D%3D"
EXAMPLE_1 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/got.png?token=AE7-yqB3eovWRUCS1YL2F4C5VVhn6TYfks5XS9bpwA%3D%3D"
EXAMPLE_2 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/econ100.png?token=AE7-ytr0TOB50ZthzYcnBCyaVps0fVJVks5XS9ycwA%3D%3D"

ABOUT_0 = "https://www.google.com/logos/2012/haring-12-hp.png"
ABOUT_1 = "https://s-media-cache-ak0.pinimg.com/736x/40/d4/7b/40d47b9ce63fae42b1ed196b11481bf6.jpg"


#POST_BACK
POST_BACK_TEMPLATE = "USER_PAYLOAD_%s"
