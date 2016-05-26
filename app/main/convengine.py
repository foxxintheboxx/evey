

import requests


from .. import db
from ..models import User, Message, Event, Calendar, Conversation
from config import WIT_API, WIT_APP_ID, WIT_SERVER
from const import EXAMPLE_0, EXAMPLE_1, EXAMPLE_2, \
                   ABOUT_0, ABOUT_1, POSTBACK_TEMPLATE, \
                   ONBOARDING_IMG_0, ONBOARDING_IMG_1, \
                   ONBOARDING_IMG_2, CALENDAR_IMG


class WitEngine(object):

    def __init__(self, app_token, server_token,
                 content_type='application/json'):
        self.app_token = app_token
        self.server_token = server_token
        self.content_type = content_type

    def make_header(self, headers={}):
        default_header = {'Authorization': 'Bearer ' + self.server_token,
                          'Accept': 'application/json'}
        for key in headers.keys():
            default_header[key] = headers[key]
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
        if q is not None:
            query_url += "&q=%s" % q
        query_url = self.__add_params__(params, query_url)
        headers = self.make_header(headers)
        return requests.post(query_url, headers=headers).json()


    def __add_params__(self, params, query_url):
        for key in params.keys():
            query_url += "&%s=%s" % (key, self.remove_space(str(params[key])))
        return query_url


    def remove_space(self, query):
        return query.replace(' ', '%20')

PLZ_SLOWDOWN = ("I'm sorry %s, but currently I am wayy better "
                "at understanding one request at a time. So "
                "plz only text me 1 thing at a time")
SIGNUP = ("Hey %s, my name is Evey. I help ppl make, schedule and manage"
          " their events! First off can you login with facebook? It helps"
          " me manage you and your friend's events."
          "Plz do this here: https://eveyai.herokuapp.com")
WAIT = ("OK %s, Thanks for registering.")
ONBOARDING_0 = ("Lets get started with how I work! exciting.")
ONBOARDING_1 = ("To make an event text me a sentence starting with "
                "make' or 'schedule'. Like these examples:")
ONBOARDING_2 = ("OK %s, after you make an event. I can help "
                "schedule a time that works for both you and your ppl")
ONBOARDING_3 = ("I'll send you a link associated with you event and you"
                " can share w/ your ppl.")
ONBOARDING_4 = ("Oh oops, I forgot something! if you want see your events,"
                " just text me 'events', and if you need any instructions"
                " again just text me 'help'")

HELP_MSG_0 = ("Hi %s, \n" + ONBOARDING_1)
HELP_MSG_1 = ("to see your events just text me 'events' or 'e'")

NON_EVENT_RESPONSE = ("I'm sorry %s, I didnt understand your msg."
                      " if you're trying to make an event, plz"
                      " start your sentence with 'make' or 'schedule'"
                      " otherwise text 'events' to see your events,"
                      " and 'help' for more info")

ONBOARDING_POSTBACK_1 = POSTBACK_TEMPLATE % "ONBOARD:1"
ONBOARDING_POSTBACK_2 = POSTBACK_TEMPLATE % "ONBOARD:2"
TUTORIAL_POSTBACK_0 = POSTBACK_TEMPLATE % "TUTORIAL:0"
TUTORIAL_POSTBACK_1 = POSTBACK_TEMPLATE % "TUTORIAL:1"

MSG_BODY = "message_body"
MSG_SUBJ = "message_subject"
LOCAL = "local_search_query"
DATE = "datetime"

class EveyEngine(WitEngine):

    def __init__(self, first_name, user):
        super(EveyEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
        self.user_name = first_name
        self.user = user
        self.postback_func = {ONBOARDING_POSTBACK_1: self.onboarding_1,
                              ONBOARDING_POSTBACK_2: self.onboarding_2}



    def understand(self, msgs):
        if len(msgs) == 0:
            return []
        if self.user is None:
            return [self.text_message(SIGNUP % self.user_name)]
        if len(msgs) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        if self.user.did_onboarding == 0:
            return self.onboarding_0()
        elif msgs[0] == "site visit":
            msg = "hi %s thanks for visiting my website" % self.user_name
            return [self.text_message(msg)]
        elif self.user.did_onboarding == 1:
            msg0 = ("plzz finish the how-to. I want to make"
                   " sure you know how I work")
            msg1 = ("it seems your at how to make events. Heres a recap")
            msgs = [self.text_message(msg0), self.text_message(msg1)]
            msgs.extend(self.onboarding_1())
            return msgs
        elif self.user.did_onboarding == 2:
            msg0 = ("plzz finish the how-to by clicking the 'Ok let's go'"
                    "button at the end of the following messages."
                   " I want to make sure you know how I work")
            msgs = [self.text_message(msg0)]
            msgs.extend(self.onboarding_1())
            return msgs
        msg = msgs[0]
        if msg == "e" or msg == "events":
            text = ("hi %s, gimme a second to fetch your events for this"
                   " week")
            return [self.text_message(text % self.user.user_name)]
        if msg == "h" or msg == "help":
            return [self.text_message(HELP_MSG_0),
                    self.usage_examples(),
                    self.text_message(HELP_MSG_1)]
        msg_data = self.message(msgs[0])
        return self.determine_response(msg_data)

    def determine_response(self, msg_data):
        entities = msg_data["entities"]
        print(entities)
        if "event" not in entities:
            return [self.text_message(NON_EVENT_RESPONSE)]
        if (entities.get("message_body") is None and
            entities.get("message_subject") is None):
            return [self.text_message("What do you wanna call the event?")]
        return self.event_creation(entities)

    def event_creation(self, entities):
        title = entities.get(MSG_SUBJ)
        if title is None:
            title = entities.get(MSG_BODY)
        title = title[0]["value"]
        buttons_msg0 = [self.make_button("postback",
                                         "share",
                                         "SHARE")]
        buttons_msg1 = [self.make_button("postback",
                                         "cancel",
                                         "CANCEL")]
        subtitle = ""
        if LOCAL in entities:
            subtitle = "Where: %s" % entities[LOCAL][0]["value"]
        else:
            buttons_msg1.append(self.make_button("postback",
                                                 "add location",
                                                 "ADD_LOCATION"))
        date_exists = False
        if DATE in entities:
            date_exists = True
            subtitle += " When: %s" % entities[DATE][0]["value"]
            buttons_msg1.append(self.make_button("postback",
                                                 "change date",
                                                  "CHANGE_DATE"))

        msg_elements = [self.make_generic_element(title=title,
                                                 subtitle=subtitle,
                                                 img_url=CALENDAR_IMG,
                                                 buttons=buttons_msg0),
                        self.make_generic_element("options",
                                                  buttons=buttons_msg1)]
        evey_resp = [self.generic_attachment(msg_elements)]
        if date_exists is False:
            text = "What times are you free for %s" % title
            evey_resp.append(self.text_message(text))
        return evey_resp

    def handle_postback(self, keys):
        if len(keys) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        return self.postback_func[keys[0]]()

    def onboarding_0(self):
        """
          this is only called once during onboarding
        """
        self.user.did_onboarding = 1
        self.save()
        payloads = [ONBOARDING_POSTBACK_1]
        onboarding_part1_button  = [self.make_button(type_="postback",
                                                     title="OK",
                                                     payload=payloads[0])]

        return [self.text_message(WAIT % self.user_name),
                self.button_attachment(ONBOARDING_0, onboarding_part1_button)]

    def onboarding_1(self):
        self.user.did_onboarding = 2
        self.save()
        usage_msg = self.usage_examples()
        payloads = [ONBOARDING_POSTBACK_2]
        onboarding_part2_button  = [self.make_button(type_="postback",
                                                     title="How?",
                                                     payload=payloads[0])]

        part_2_msg = self.button_attachment(ONBOARDING_2 % self.user_name,
                                            onboarding_part2_button)
        usage_msg = self.usage_examples()
        return [self.text_message(ONBOARDING_1),
                usage_msg, part_2_msg]


    def onboarding_2(self):
        self.user.did_onboarding = 3
        self.save()

        tutorial_text = "Do you want to try making an example event?"
        tutorial_buttons = [self.make_button(type_="postback",
                                             title="No thanks, I got it",
                                             payload=TUTORIAL_POSTBACK_0),
                            self.make_button(type_="postback",
                                             title="Ok, lets try it",
                                             payload=TUTORIAL_POSTBACK_1)]
        tutorial = self.button_attachment(text=tutorial_text,
                                          buttons=tutorial_buttons)
        onboarding_imgs = self.onboarding_attachments()
        return [self.text_message(ONBOARDING_3),
                onboarding_imgs, self.text_message(ONBOARDING_4)]


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

    def onboarding_attachments(self):
        titles = ["event link to share with your friends",
                  "stop worrying about choosing a time",
                  "I'll let you know the best time"]
        img_urls = [ONBOARDING_IMG_0,
                    ONBOARDING_IMG_1,
                    ONBOARDING_IMG_2]
        elements = []
        for i in range(3):
           elements.append(self.make_generic_element(titles[i],
                                                    img_url=img_urls[i]))
        return self.generic_attachment(elements)

    def about(self):
        titles = ["I'll chat with your ppl",
                  "Tell you the right time for EVEYbody"]
        subtitles = ["Evey chat personally the ppl invited & coordinate a free time",
                    "Evey will text you back with the details that work eveyone"]
        img_urls = [ABOUT_0, ABOUT_1]
        elements = []
        for i in range(2):
            elements.append(self.make_generic_element(title=titles[i],
                                                      subtitle=subtitles[i],
                                                      img_url=img_urls[i]))
        return self.generic_attachment(elements)

    def text_message(self, text):
      return {"text": text}

    def button_attachment(self, text, buttons):
        return {"attachment": {
                  "type": "template",
                  "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                  }
                }
              }

    def generic_attachment(self, elements):
        return {"attachment": {
                  "type": "template",
                  "payload": {
                    "template_type": "generic",
                    "elements": elements
                    }
                  }
                }

    def make_generic_element(self, title, subtitle="",
                                    img_url="",
                                    buttons=[]):
        element = {"title": title}
        if len(subtitle) > 0:
            element["subtitle"] = subtitle
        if len(img_url) > 0:
            element["image_url"] = img_url
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
