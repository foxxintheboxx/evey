from dateutil.parser import parse
import json
from . import db
from .witengine import WitEngine
from .fbapimethods import FBAPI
from .models import User, Message, Event, Calendar, Conversation, \
                    Datepoll, Locationpoll
from .utils import fetch_user_data
from config import WIT_APP_ID, WIT_SERVER
from .utils import generate_hash
from const import EXAMPLE_0, EXAMPLE_1, EXAMPLE_2,\
                   WHEN_EMOJI, WHERE_EMOJI, OTHER_EMOJI, \
                   MSG_BODY, MSG_SUBJ, LOCAL, DATE, \
                   EVENT_POSTBACKS, PEOPLE_EMOJI, \
                   EVEY_URL, GUY_EMOJI, CONFIRM_POSTBACK,\
                   CANCEL_LOCATION_POSTBACK

PLZ_SLOWDOWN = ("I'm sorry %s, but currently I am wayy better "
                "at understanding one request at a time. So "
                "plz only text me 1 thing at a time")
SIGNUP = ("First off, it doesnt look like you have an account yet."
          "Plz sign up so we can get started!")
WAIT = ("OK %s, Thanks for registering.")
ONBOARDING_1 = ("To make an event text me a sentence starting with "
                "'make'. Like this:")
ONBOARDING_2 = ("I can then help schedule a time that works for both "
                "you and your ppl")
ONBOARDING_3 = ("To invite ppl, forward them a link to the event")
ONBOARDING_4 = ("Thats it!")

HELP_MSG_0 = ("Hi %s, \n" + ONBOARDING_1)
HELP_MSG_1 = ("to see your events just text me 'events' or 'e'")

NON_EVENT_RESPONSE = ("I didn't quite get that.\n"
                      "> 'make' to make an event\n"
                      "> 'find' <event name>\n"
                      "> 'events' to see all your events")


class EveyEngine(WitEngine, FBAPI):

    def __init__(self, first_name, user, messenger_uid):
        super(EveyEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
        self.user_name = first_name
        self.messenger_uid = messenger_uid
        self.user = user
        self.postback_func = {EVENT_POSTBACKS["share"]: self.get_event_link,
                              EVENT_POSTBACKS["who"]: self.see_people_in_event,
                              EVENT_POSTBACKS["back"]: self.back_to_callback,
                              EVENT_POSTBACKS["when"]: self.collab_date_callback,
                              EVENT_POSTBACKS["where"]: self.edit_location,
                              CONFIRM_POSTBACK: self.confirm_location_change,
                              CANCEL_LOCATION_POSTBACK: self.cancel_location_edit}

    def understand(self, msgs):
        if len(msgs) == 0:
            return []
        if self.user is None:
            return [self.signup_attachment()]
        if len(msgs) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        if self.user.did_onboarding == 0 or msgs[0].lower() == "help":
            return self.onboarding_1()
        if len(self.user.is_editing_location) > 0:
            return self.handle_edit_location(msgs[0])
        if msgs[0] == "site visit":
            return []
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
        event = self.create_event(entities)
        return [self.event_attachment(event.event_hash, event=event)]


    def create_event(self, entities):
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
        objects = [event, calendar]
        if DATE in entities:
            dateobj = parse(entities[DATE][0]["value"])
            datepoll = Datepoll()
            datepoll.users.append(curr_user)
            datepoll.datetime = dateobj
            event.date_polls.append(datepoll)
            objects.append(datepoll)
        if LOCAL in entities:
            where_str = str(entities[LOCAL][0]["value"])
            words = self.capitalize_first_letter(where_str.split(" "))
            where_str = " ".join(words)
            locationpoll = Locationpoll()
            locationpoll.name = where_str
            locationpoll.users.append(curr_user)
            event.location_polls.append(locationpoll)
            objects.append(locationpoll)
        self.save(objects)
        return event


    def event_attachment(self, event_hash, event=None):
        if event == None:
            event = self.event_from_hash(event_hash)

        title = event.title
        postbacks = self.format_event_postbacks(EVENT_POSTBACKS,
                                                event.event_hash)
        buttons_msg0 = [self.make_button("postback", "share",
                                         postbacks["share"]),
                       self.make_button("postback", "avail " + WHEN_EMOJI + "s",
                                         postbacks["when"])]
        buttons_msg1 = [self.make_button("postback","edit " + WHERE_EMOJI,
                                         postbacks["where"]),
                        self.make_button("postback",
                                          PEOPLE_EMOJI,
                                         postbacks["who"]),
                        self.make_button("postback",
                                          "add to Google Cal",
                                          "TODO")]

        subtitle = "Best so far"
        date_exists = False
        top_date = event.get_top_date()
        attendees = event.attendees()
        if top_date != None:
            dateobj = top_date.datetime
            votes = top_date.votes()
            subtitle += " (%s/%s)" % (votes, len(attendees))
            date_str = self.format_dateobj(dateobj)
            subtitle += "\n%s %s\n" % (WHEN_EMOJI, date_str)
        else:
            subtitle += "\n%s none yet\n" % (WHEN_EMOJI)
        top_location = event.get_top_local()
        if top_location != None:
            where_str = str(top_location.name)
            subtitle += "%s %s\n" % (WHERE_EMOJI, where_str)
        else:
            subtitle += "%s none yet\n" % (WHERE_EMOJI)
        msg_elements = [self.make_generic_element(title=title,
                                                 subtitle=subtitle,
                                                 buttons=buttons_msg0),
                        self.make_generic_element("... More",
                                                  buttons=buttons_msg1)]
        evey_resp = self.generic_attachment(msg_elements)
        return evey_resp



    def get_event_link(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        title = event.title
        url = EVEY_URL + "/ev/" + event.event_hash
        text = "View/Edit details: \"%s\"\n%s" % (title, url)
        return [self.text_message(text)]

    def see_people_in_event(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        calendars = event.calendars
        ppl_attachments = []
        for person in event.attendees():
            messenger_uid = person.messenger_uid
            user_data = fetch_user_data(messenger_uid)
            el = self.make_generic_element(title=person.name,
                                           img_url=user_data["profile_pic"])
            ppl_attachments.append(el)
        evey_rsp = self.text_message(("these ppl were invited"))
        return [evey_rsp, self.generic_attachment(ppl_attachments),
                self.back_to_button(event.event_hash, event)]

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


    def onboarding_1(self):
        self.user.did_onboarding = 2
        self.save([self.user])
        usage_msg = self.usage_examples()
        return [self.text_message(ONBOARDING_1), usage_msg]

    def collab_date_callback(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        date_polls = event.date_polls.all()
        text = ""
        if len(date_polls) == 0:
          text = "Looks like no one has added any of their availabilities yet"
        else:
          for poll in date_polls:
            votes = ""
            if poll.votes() >= 4:
              votes = "%s X %s" % (poll.votes(), GUY_EMOJI)
            else:
              votes = GUY_EMOJI * poll.votes()
            dateobj = poll.datetime
            date_str = self.format_dateobj(dateobj)
            text += "%s, %s\n" % (date_str, votes)
        postbacks = self.format_event_postbacks(dict(EVENT_POSTBACKS),
                                                event.event_hash)
        add_button = self.make_button(type_="postback", title="add " + WHEN_EMOJI,
                                       payload="TODO")
        remove_button = self.make_button(type_="postback", title="remove " + WHEN_EMOJI,
                                       payload="TODO")
        back_button = self.make_button(type_="postback", title="event menu",
                                       payload=postbacks["back"])
        return [self.button_attachment(text=text, buttons=[add_button,
                                                          remove_button,
                                                          back_button])]

    def edit_location(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        location_poll = event.location_polls.first()
        text = "Text me the new location you want. Or, press cancel"
        self.user.is_editing_location = event.event_hash
        self.save([self.user])
        postbacks = self.format_event_postbacks(dict(EVENT_POSTBACKS),
                                                event.event_hash)

        cancel_button = self.make_button(type_="postback", title="cancel",
                                         payload=CANCEL_LOCATION_POSTBACK)
        return [self.button_attachment(text=text, buttons=[cancel_button])]

    def handle_edit_location(self, msg):
        words = self.capitalize_first_letter(msg.split(" "))
        location = " ".join(words)
        text = "Is this correct? %s" % location
        confirm_postback = self.format_postback(CONFIRM_POSTBACK,
                                                {"name": location})
        confirm_button = self.make_button(type_="postback", title="Yes",
                                          payload=confirm_postback)
        cancel_button = self.make_button(type_="postback", title="cancel",
                                         payload=CANCEL_LOCATION_POSTBACK)
        return [self.button_attachment(text=text, buttons=[confirm_button,
                                                           cancel_button])]

    def confirm_location_change(self, event_json):
        event_hash = self.user.is_editing_location
        name = event_json["name"]
        self.user.is_editing_location = ""
        event = self.event_from_hash(event_hash)
        last_poll = event.location_polls.first()
        if last_poll:
          self.delete([last_poll])

        new_poll = Locationpoll()
        new_poll.name = name
        event.location_polls.append(new_poll)
        self.save([self.user, event, new_poll])
        return [self.text_message(text="success!"),
                self.event_attachment(event_hash, event)]

    def cancel_location_edit(self):
        event_hash = self.user.is_editing_location
        self.user.is_editing_location = ""
        self.save([self.user])
        return [self.text_message("Ok canceled"), self.event_attachment(event_hash)]

    def back_to_button(self, event_hash, event=None):
        if event == None:
            event = self.event_from_hash(event_hash)
        text = "Back to \"%s\"" % event.title
        title = event.title
        if len(event.title) > 20:
            title = title[:17] + "..."
        postbacks = self.format_event_postbacks(dict(EVENT_POSTBACKS),
                                                event.event_hash)

        back_button = self.make_button(type_="postback", title=title,
                                         payload=postbacks["back"])
        return self.button_attachment(text=text,
                                      buttons=[back_button])
    def back_to_callback(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        return [self.event_attachment(event.event_hash, event)]


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



    def format_event_postbacks(self, postbacks, event_hash):
        postbacks = dict(postbacks)
        for key in postbacks.keys():
          event_data = {"event_hash": event_hash}
          postbacks[key] = self.format_postback(postbacks[key], event_data)
        return postbacks

    def format_postback(self, postback, data_dict):
        return postback + "$" +  json.dumps(data_dict)

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

    def delete(self, models):
        for model in models:
            db.session.delete(model)
        db.session.commit()

    def event_from_hash(self, event_hash):
        return Event.query.filter(Event.event_hash==event_hash).first()

    def capitalize_first_letter(self, words):
        for i in range(len(words)):
            words[i] = words[i][0].upper() + words[i][1:]
        return words
