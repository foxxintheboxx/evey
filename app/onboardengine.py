from . import db
from .witengine import WitEngine
from .fbapimethods import FBAPI
from config import WIT_APP_ID, WIT_SERVER
from const import EXAMPLE_0, EXAMPLE_1, EXAMPLE_2, EVEY_URL, HELP
from .utils import save

ONBOARDING_1 = ("To make an event text me a sentence starting with "
                "'make'. Like this:")
ONBOARDING_2 = ("I can then help schedule a time that works for both "
                "you and your ppl")
ONBOARDING_3 = ("To invite ppl, forward them a link to the event")
ONBOARDING_4 = ("Thats it!")
SIGNUP = ("First off, it doesnt look like you have an account yet."
          "Plz sign up so we can get started!")

class OnboardEngine(WitEngine, FBAPI):

  def __init__(self, first_name, user, messenger_uid):
    super(OnboardEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
    self.user_name = first_name
    self.user = user
    self.messenger_uid = messenger_uid

  def onboarding_1(self):
    self.user.did_onboarding = 2
    save([self.user])
    return [self.text_message(HELP)]

