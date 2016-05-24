

import json
import requests
import traceback


from .. import db
from ..models import User, Message, Event, Calendar, Conversation
from config import WIT_API, WIT_APP_ID, WIT_SERVER
from const import EXAMPLE_0, EXAMPLE_1, EXAMPLE_2, \
                   ABOUT_0, ABOUT_1, POSTBACK_TEMPLATE



class WitEngine(object):

  def __init__(self, app_token, server_token, content_type='application/json'):
    self.app_token = app_token
    self.server_token = server_token
    self.content_type = content_type

  def make_header(self,headers={}):
    default_header = {'Authorization': 'Bearer ' + self.server_token,
                      'Accept': 'application/json'}
    for key in params.keys():
      default_header[key] = params[key]
    return default_header

  def message(self, q, params={}, headers={}):

    query_url = WIT_API + "message"
    query_url += "?q=%s" % q
    query_url = self.__add_params__(params, query_url)
    headers = self.make_header(headers)
    return requests.get(query_url, headers=headers).json()

  def converse(self, session_id, q, params={}, headers={}):
    query_url = WIT_API + "converse"
    query_url += "?session_id=%s" % session_id
    if q != None:
      query_url += "&q=%s" % q
    query_url = self.__add_params__(params, query_url)
    headers = self.make_header(headers)
    return requests.post(query_url, headers=headers).json()


  def __add_params__(self, params, query_url):
    for key in params.key():
      query_url += "&%s=%s" % (key, self.remove_space(str(params[key])))
    return query_url


  def remove_space(self, query):
    return query.replace(' ', '%20')

PLZ_SLOWDOWN = ("I'm sorry %s, but currently I am wayy better "
                "at understanding one request at a time. So "
                "plz only text me 1 thing at a time")
SIGNUP = ("Hey %s, signing up with facebook helps me connect you "
         "with your friends. Plz link fb at https://eveyai.herokuapp.com")
WAIT = ("OK %s, Thanks for registering. I\'m not totally developed"
       "yet -- Stay Tuned")

class EveyEngine(WitEngine):

  def __init__(self, first_name, user):
    super(EveyEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
    self.user_name = first_name
    self.user = user

  def understand(self, msgs):
    if len(msg) == 0:
      return []
    if self.user == None:
      return [self.text_message(SIGNUP % self.user_name)]
    if len(msgs) > 1:
      return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
    if self.user.did_onboarding == False:
      self.user.did_onboarding = 1
      self.save()
      return self.onboarding()
    else:
      return [self.text_message(WAIT % self.user_name)]
    resp = self.converse(session_id, msg)
    while (msg["type"] not in ["msg", "stop"]):
      resp = self.convserse(session_id, None)
    return msg.get("msg")



  def onboarding(self):
    """
      this is only called once during onboarding
    """
    usage_msg = self.usage_examples()
    about_msg = self.about()
    payloads = [POSTBACK_TEMPLATE % "TUTORIAL:NO",
                POSTBACK_TEMPLATE % "TUORIAL:YES"]
    tutorial_buttons = [self.make_button(type_="postback",
                                         title="No thanks, I got it",
                                         payload=payloads[0]),
                        self.make_button(type_="postback",
                                         title="Ok, lets try it",
                                         payload=payloads[1])]

    tutorial_text = "Do you want to try making an example event?"
    try_tutorial = self.button_attachment(tutorial_text,
                                          tutorial_buttons)
    return [usage_msg, about_msg]

  def tutorial(self):
    evey_dialogue = ["ok now send me this fake event",
                     "(talking to your ppl",
                     ".",
                     "..",
                     "...30 min later)",
                    ]

    pretend_event = "make a dolores homie picnic"


  def usage_examples(self):
    titles = ["Tell me about event like this...",
              "...or, like this ...",
              "... or this"]
    img_urls = [EXAMPLE_0, EXAMPLE_1, EXAMPLE_2]
    elements = []
    for i in range(3):
      elements.append(self.make_generic_element(titles[i],
                                                img_url=img_urls[i]))
    return self.generic_attachment(elements)

  def about(self):
    titles = ["I'll chat with your ppl",
              "Tell you the right time for EVEYbody"]
    subtitle = ["Evey chat personally the ppl invited & coordinate a free time",
                "Evey will text you back with the details that work eveyone"]
    img_urls = [ABOUT_0, ABOUT_1]
    elements = []
    for i in range(2):
        elements.append(self.make_generic_element(title[i],
                                                  subtitles=subtitles[i],
                                                  img_url=img_urls[i]))
    return self.generic_attachment(elements)

  def text_message(self, text):
    return {"text": text}

  def button_attachment(self, text, buttons):
    return {"attachement": {
              "type": "template",
              "payload": {
                "template_type": "button",
                "text": text,
                "buttons": buttons
              }
            }
          }

  def generic_attachment(self, elements):
    return {"attachement": {
              "type": "template",
              "payload": {
                "template_type": "generic",
                "elements": elements
                }
              }
            }

  def make_generic_element(self, title, subtitle="",
                                  imge_url="",
                                  buttons=[]):
    element = {"title": title}
    if len(subtitle) > 0:
      element["subtitle"] = subtitle
    if len(imge_url) > 0:
      element["image_url"] = image_url
    if len(buttons) > 0:
      element["buttons"] = buttons
    return element

  def make_button(self, type_, title, payload):
    dict_ = {"type": type_,
             "title": title}
    if type_ == "web_url":
      dict_["url"] = payload
    if type_ == "postback":
      dict_["payload"] = payload
    return dict_

  def save(self):
    db.session.add(self.user)
    db.session.commit()
