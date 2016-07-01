from . import db
from .witengine import WitEngine
from .fbapimethods import FBAPI
from config import WIT_APP_ID, WIT_SERVER
from const import EXAMPLE_0, EXAMPLE_1, EXAMPLE_2, EVEY_URL, HELP
from .utils import save


class OnboardEngine(WitEngine, FBAPI):

  def __init__(self, first_name, user, messenger_uid):
    super(OnboardEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
    self.user_name = first_name
    self.user = user
    self.messenger_uid = messenger_uid

  def onboarding_1(self):
    self.user.did_onboarding = 2
    save([self.user])
    return [self.text_message(HELP % str(self.user_name))]

