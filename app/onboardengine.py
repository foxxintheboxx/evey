from . import db
from .witengine import WitEngine
from .fbapimethods import FBAPI
from config import WIT_APP_ID, WIT_SERVER
from const import EXAMPLE_0, EXAMPLE_1, EXAMPLE_2

ONBOARDING_1 = ("To make an event text me a sentence starting with "
                "'make'. Like this:")
ONBOARDING_2 = ("I can then help schedule a time that works for both "
                "you and your ppl")
ONBOARDING_3 = ("To invite ppl, forward them a link to the event")
ONBOARDING_4 = ("Thats it!")

class OnboardEngine(WitEngine, FBAPI):

  def __init__(self, first_name, user):
    super(OnboardEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
    self.user_name = first_name
    self.user = user

  def onboarding_1(self):
    self.user.did_onboarding = 2
    self.save([self.user])
    usage_msg = self.usage_examples()
    return [self.text_message(ONBOARDING_1), usage_msg]

  def usage_examples(self):
    titles = [ONBOARDING_2,
              ONBOARDING_3,
              ONBOARDING_4,]
    img_urls = [EXAMPLE_0, EXAMPLE_1, EXAMPLE_2]
    elements = []
    for i in range(3):
      elements.append(self.make_generic_element(titles[i],
                                                img_url=img_urls[i]))
    return self.generic_attachment(elements)

  def save(self, models):
    for model in models:
      db.session.add(model)
    db.session.commit()
