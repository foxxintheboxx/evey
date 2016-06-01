from dateutil.parser import parse
import json
from . import db
from .witengine import WitEngine
from .fbapimethods import FBAPI
from .models import User, Message, Event, Calendar, Conversation
from .utils import fetch_user_data
from config import WIT_APP_ID, WIT_SERVER
from .utils import generate_hash
from const import EXAMPLE_0, EXAMPLE_1, EXAMPLE_2, \
                   ABOUT_0, ABOUT_1, ONBOARDING_POSTBACK_1, \
                   ONBOARDING_IMG_0, ONBOARDING_IMG_1, \
                   ONBOARDING_IMG_2, CALENDAR_IMG, \
                   WHEN_EMOJI, WHERE_EMOJI, OTHER_EMOJI, \
                   MSG_BODY, MSG_SUBJ, LOCAL, DATE, \
                   EVENT_POSTBACKS, PEOPLE_EMOJI, \
                   ONBOARDING_POSTBACK_2, EVEY_URL

PLZ_SLOWDOWN = ("I'm sorry %s, but currently I am wayy better "
                "at understanding one request at a time. So "
                "plz only text me 1 thing at a time")
SIGNUP = ("First off, it doesnt look like you have an account yet."
          "Plz sign up so we can get started!")
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


class EveyEngine(WitEngine, FBAPI):

    def __init__(self, first_name, user, messenger_uid):
        super(EveyEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
        self.user_name = first_name
        self.messenger_uid = messenger_uid
        self.user = user
        self.postback_func = {ONBOARDING_POSTBACK_1: self.onboarding_1,
                              ONBOARDING_POSTBACK_2: self.onboarding_2,
                              EVENT_POSTBACKS["share"]: self.get_event_link,
                              EVENT_POSTBACKS["who"]: self.see_people_in_event}

    def understand(self, msgs):
        if len(msgs) == 0:
            return []
        if self.user is None:
            return [self.signup_attachment()]
        if len(msgs) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        if self.user.did_onboarding == 0:
            return self.onboarding_0()
        elif msgs[0] == "site visit":
            return []
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
        if msg.lower() == "e" or msg.lower() == "events":
            text = ("hi %s, gimme a second to fetch your events for this"
                   " week")
            return [self.text_message(text % self.user.user_name)]
        if msg.lower() == "h" or msg.lower() == "help":
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
        title_words = self.capitalize_first_letter(title.split(" "))
        title = " ".join(title_words)
        curr_user = self.current_user()
        calendar = curr_user.calendar
        event = Event(title=title)
        event.event_hash = generate_hash()
        calendar.events.append(event)
        self.save([event, calendar])
        postbacks = self.format_event_postbacks(EVENT_POSTBACKS,
                                                event.event_hash)
        buttons_msg0 = [self.make_button("postback",
                                         "share",
                                         postbacks["share"])]
        buttons_msg1 = [self.make_button("postback",
                                         "collab on " + WHEN_EMOJI + "s",
                                         postbacks["where"]),
                        self.make_button("postback",
                                         "collab on " + WHERE_EMOJI + "s",
                                         postbacks["when"]),
                        self.make_button("postback",
                                          PEOPLE_EMOJI,
                                         postbacks["who"])]

        subtitle = "Top\n"
        date_exists = False
        if DATE in entities:
            date_exists = True
            dateobj = parse(entities[DATE][0]["value"])
            date_str = self.format_dateobj(dateobj)
            subtitle += "%s %s\n" % (WHEN_EMOJI, date_str)
        else:
            subtitle += "%s none yet\n" % (WHEN_EMOJI)

        if LOCAL in entities:
            where_str = str(entities[LOCAL][0]["value"])
            words = self.capitalize_first_letter(where_str.split(" "))
            where_str = " ".join(words)
            subtitle += "%s %s\n" % (WHERE_EMOJI, where_str)
        else:
            subtitle += "%s none yet\n" % (WHERE_EMOJI)

        msg_elements = [self.make_generic_element(title=title,
                                                 subtitle=subtitle,
                                                 buttons=buttons_msg0),
                        self.make_generic_element("Deets Preview",
                                                  buttons=buttons_msg1)]
        evey_resp = [self.generic_attachment(msg_elements)]
#        if date_exists is False:
#           text = "What times are you free for %s" % title
#           evey_resp.append(self.text_message(text))
        return evey_resp

    def get_event_link(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        title = event.title
        url = EVEY_URL + "/events/" + event.event_hash
        text = "View/Edit details: \"%s\"\n%s" % (title, url)
        return [self.text_message(text)]

    def see_people_in_event(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        calendars = event.calendars
        attendees = [cal.user for cal in event.calendars]
        ppl_attachments = []
        for person in attendees:
            messenger_uid = person.messenger_uid
            user_data = fetch_user_data(messenger_uid)
            el = self.make_generic_element(title=person.name,
                                           img_url=user_data["profile_pic"])
            ppl_attachments.append(el)
        evey_rsp = self.text_message(("Np, so far these are the ppl checking out"
                                      " this event"))
        return [evey_rsp, self.generic_attachment(ppl_attachments)]


    def back_to_event_menu(self, event_hash):
        pass

    def signup_attachment(self):
        url = EVEY_URL + "/register/" + self.messenger_uid
        signup_button = self.make_button(type_="web_url", title="Sign Up!",
                                         payload=url)
        return self.button_attachment(text=SIGNUP,
                                      buttons=[signup_button])

    def handle_postback(self, keys):
        if len(keys) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        print(str(keys[0]))
        postback_data = str(keys[0]).split('$')
        if len(postback_data) > 1:
            data = json.loads(postback_data[1])
            return self.postback_func[postback_data[0]](data)
        return self.postback_func[postback_data[0]]()

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

    def collab_date_postback(self):
        pass

    def collab_location_postback(self):
        pass

    def onboarding_2(self):
        self.user.did_onboarding = 3
        self.save()
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

    def format_event_postbacks(self, postbacks, event_hash):
        postbacks = dict(postbacks)
        for key in postbacks.keys():
          event_data = {"event_hash": event_hash}
          postbacks[key] = postbacks[key] + "$" +  json.dumps(event_data)
        return postbacks

    def format_dateobj(self, dateobj):
        ampm = "am"
        if dateobj.hour > 12:
            ampm = "pm"
        minute = ""
        if dateobj.minute > 0:
            minutes = str(dateobj.minute)
            if len(minute) < 2:
                minutes = "0" + minutes
            minute = ":" + minutes
        datestr = dateobj.strftime("%a %m/%d  at %I")
        datestr.replace("0", "")
        datestr += minute + ampm
        return datestr

    def current_user(self):
        return User.query.filter(User.messenger_uid==self.messenger_uid).first()

    def save(self, models):
        for model in models:
            db.session.add(model)
        db.session.commit()

    def event_from_hash(self, event_hash):
        return Event.query.filter(Event.event_hash==event_hash).first()

    def capitalize_first_letter(self, words):
        for i in range(len(words)):
            words[i] = words[i][0].upper() + words[i][1:]
        return words
