import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db'))
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SECRET_KEY = 'development key'
# messenger access toke
TOKEN = "EAAYbvNuO44cBAGcjOnLfqTR0RtMVUVvZBZAIkFaEGNifKqC6kIPPDuYdwDdKaS7c9I12gGohd0NPFmoIGF9ikZCmHBZCYi7Tq1SKDwMs6sRBUofqGTSdyhFLB949kZBVHaW9h6ZCezKaRY4IPxvALDLGvCJDjzxMoZD"

WEBHOOK = "518aaf94cff67b8498a4a811b91a50be40c75de1398f52b066"
WEBHOOK_TOKEN = 'eveytesting'
FACEBOOK_APP_ID = '423366987795505'

FACEBOOK_APP_SECRET = 'd5163109796d51e5d875ac56797c11c6'
