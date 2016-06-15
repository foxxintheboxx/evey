from dateutil.parser import parse
from dateutil.tz import *
import json, re
from . import db
from .witengine import WitEngine
from .fbapimethods import FBAPI
from .models import User, Message, Event, Calendar, Conversation, \
                    Datepoll, Locationpoll
from .utils import fetch_user_data, format_ampm, string_to_day, save, delete, \
                   encode_unicode
from config import WIT_APP_ID, WIT_SERVER
from .onboardengine import OnboardEngine
from .utils import generate_hash
from const import  WHEN_EMOJI, WHERE_EMOJI, OTHER_EMOJI, EVEY_URL, \
                   MSG_BODY, MSG_SUBJ, LOCAL, DATE, EVENT_POSTBACKS, \
                   PEOPLE_EMOJI, GUY_EMOJI, CONFIRM_POSTBACK,\
                   CANCEL_LOCATION_POSTBACK, ADD_TIME_POSTBACK, \
                   REMOVE_TIME_POSTBACK, NUM, DAY_ABRV, CANCEL_ADD_TIME, \
                   CANCEL_REMOVE_TIME, GREEN_CHECK_EMOJI, CAL_EMOJI, \
                   RED_X_EMOJI, CANCEL, ELLIPSE, DOWN_ARROW, BLACK_CIRCLE, \
                   EMOJI_NUM

PLZ_SLOWDOWN = ("I'm sorry %s, but currently I am wayy better "
                "at understanding one request at a time. So "
                "plz only text me 1 thing at a time")
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
        self.onboarder = OnboardEngine(first_name, user, messenger_uid)
        self.postback_func = {EVENT_POSTBACKS["share"]: self.get_event_link,
                              EVENT_POSTBACKS["who"]: self.see_people_in_event,
                              EVENT_POSTBACKS["back"]: self.back_to_callback,
                              EVENT_POSTBACKS["when"]: self.collab_date_callback,
                              EVENT_POSTBACKS["where"]: self.edit_location,
                              EVENT_POSTBACKS["add_time"]: self.add_date_callback,
                              EVENT_POSTBACKS["remove_time"]: self.remove_date_callback,
                              CONFIRM_POSTBACK: self.confirm_location_change,
                              CANCEL_REMOVE_TIME: self.cancel_date_edit,
                              CANCEL_ADD_TIME: self.cancel_date_edit,
                              CANCEL_LOCATION_POSTBACK: self.cancel_location_edit}

    def understand(self, msgs):
        if len(msgs) == 0:
            return []
        if self.user is None:
            return [self.onboarder.signup_attachment()]
        if len(msgs) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        if self.user.did_onboarding == 0 or msgs[0].lower() == "help":
            return self.onboarder.onboarding_1()
        if len(self.user.is_editing_location) > 0:
            return self.handle_edit_location(msgs[0])
        if len(self.user.is_adding_time) > 0:
            return self.handle_add_time(msgs[0])
        if len(self.user.is_removing_time) > 0:
            return self.handle_remove_time(msgs[0])
        if msgs[0] == "site visit":
            return []
        msg = msgs[0]
        if msg.lower() == "e" or msg.lower() == "events":
            text = ("hi %s, gimme a second to fetch your events for this"
                   " week")
            return [self.text_message(text % self.user.user_name)]
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
        p1, p2 = self.event_attachment(event.event_hash, event=event)
        return [p1, p2]

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
            dateobj = parse(entities[DATE][0]["value"]).astimezone(tzutc())
            datepoll = Datepoll()
            datepoll.users.append(curr_user)
            datepoll.datetime = dateobj
            event.append_datepoll(datepoll)
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
        save(objects)
        return event

    def event_attachment(self, event_hash, event=None):
        if event == None:
            event = self.event_from_hash(event_hash)

        title = "%s %s" % (CAL_EMOJI, str(event.title))
        postbacks = self.format_event_postbacks(EVENT_POSTBACKS,
                                                event.event_hash)
        date_exists = False
        top_date = event.get_top_date()
        attendees = len(event.attendees())
        date = ""
        if top_date != None:
            dateobj = top_date.datetime
            votes = top_date.votes()
            date_str = self.format_dateobj(dateobj)
            date  = "%s %s" % (WHEN_EMOJI, date_str)
        else:
            date = "%s none yet" % (WHEN_EMOJI)
        top_location = event.get_top_local()
        where = ""
        if top_location != None:
            where_str = str(top_location.name)
            where = "%s %s" % (WHERE_EMOJI, where_str)
        else:
            where = "%s none yet" % (WHERE_EMOJI)
        buttons_msg0 = [self.make_button("postback", date,
                                         postbacks["when"]),
                        self.make_button("postback",
                                          PEOPLE_EMOJI + "(%s)" % attendees,
                                         postbacks["who"]),
                        self.make_button("postback", where,
                                          postbacks["where"])]

        buttons_msg1 = [self.make_button("postback", "event link",
                                         postbacks["share"])]

        msg_elements0 = [self.make_generic_element(title=title,
                                                 buttons=buttons_msg0)]
        msg_elements1 = [self.make_generic_element(title="invite friends",
                                                  buttons=buttons_msg1)]
        evey_resp = self.generic_attachment(msg_elements0)
        evey_resp1 = self.generic_attachment(msg_elements1)
        return evey_resp, evey_resp1

    def get_event_link(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        title = str(event.title)
        url = str(EVEY_URL + "ev/" + event.event_hash)
        text = CAL_EMOJI + " \"%s\" details\n %s" % (title, url)

        return [self.text_message("forward this link" + DOWN_ARROW),
                self.text_message(text)]

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
        return [self.generic_attachment(ppl_attachments),
                self.back_to_button(event.event_hash, event)]

    def handle_postback(self, keys):
        if len(keys) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        postback_data = str(keys[0]).split('$')
        if len(postback_data) > 1:
            data = json.loads(postback_data[1])
            return  self.postback_func[postback_data[0]](data)
        return self.postback_func[postback_data[0]]()

    def handle_add_time(self, msg):
        event = self.event_from_hash(self.user.is_adding_time)
        intervals = self.extract_intervals(msg)
        tokens = msg.split(" ")
        tokens = [encode_unicode(el.replace(",", "")) for el in tokens]
        numbers = []
        for t in tokens:
            try:
                numbers.append(int(t))
            except:
                continue
        polls = []
        for i in intervals:
            inter_polls = event.add_new_interval(i.get("from"), i.get("to"), self.user)
        event.sort_datepolls()
        save(event.get_datepolls())
        save([self.user, event])
        text = GREEN_CHECK_EMOJI + " I added your times!"
        text2 = self.event_times_text(event)
        return [self.text_message(text),
                self.text_message(text2),
                self.back_to_button(event.event_hash, event)]

    def handle_remove_time(self, msg):
        pass

    def collab_date_callback(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        text = self.event_times_text(event)
        postbacks = self.format_event_postbacks(dict(EVENT_POSTBACKS),
                                                event.event_hash)
        buttons = []
        remove_button = self.make_button(type_="postback", title="remove " + WHEN_EMOJI,
                                       payload=postbacks["remove_time"])
        text2 = ("To add your " + WHEN_EMOJI +  " :\n" +
                 BLACK_CIRCLE + " text me a number i.e." +
                 NUM[1] +  ", " +  NUM[2]  + "\n" +
                 BLACK_CIRCLE + " or, a new time i.e. Thu 3-4pm")
        self.user.is_adding_time = event_json["event_hash"]
        save([self.user])
        if event.user_added_time(self.user):
          buttons.append(remove_button)
        back_button = self.make_button(type_="postback", title=CANCEL,
                                       payload=CANCEL_ADD_TIME)
        buttons.append(back_button)
        return [self.text_message(text), self.button_attachment(text=text2, buttons=buttons)]

    def add_date_callback(self, event_json):
        self.user.is_adding_time = event_json["event_hash"]
        save([self.user])
        event = self.event_from_hash(event_json["event_hash"])
        text1 = self.event_times_text(event)
        return [self.text_message(text1)]

    def remove_date_callback(self, event_json):
        self.user.is_removing_time = event_json["event_hash"]
        save([self.user])
        event = self.event_from_hash(event_json["event_hash"])
        text1 = self.event_times_text(event, user=self.user)
        text2 = ("Text me:\n"
                 "> a number correspond to an above time\n"
                 "> a time within one of the above times\n")
        cancel_button = self.make_button(type_="postback", title=CANCEL,
                                         payload=CANCEL_REMOVE_TIME)
        return [self.text_message(text1), self.text_message(text=text2,
                                                            buttons=[cancel_button])]

    def event_times_text(self, event, user=None):
        date_polls = event.get_datepolls()
        text = ""
        if len(date_polls) == 0:
          text = "Looks like no one has added any of their availabilities yet"
        else:
          for poll in date_polls:
            if poll.poll_number == 2:
              text += "-"*min(len(text), 25) + "\n"
            if user != None and user not in poll.users:
              continue
            votes = ""
            if poll.votes() > 2:
              votes = "%sx%s" % (poll.votes(), GUY_EMOJI)
            else:
              votes = GUY_EMOJI * poll.votes()
            dateobj = poll.datetime
            date_str = self.format_dateobj(dateobj)
            text += "%s %s, %s\n" % (NUM[poll.poll_number], date_str, votes)
        return text

    def edit_location(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        location_poll = event.location_polls.first()
        text = "Text me a new " + WHERE_EMOJI + ". Or, press " + RED_X_EMOJI
        self.user.is_editing_location = event.event_hash
        save([self.user])
        postbacks = self.format_event_postbacks(dict(EVENT_POSTBACKS),
                                                event.event_hash)
        cancel_button = self.make_button(type_="postback", title=CANCEL,
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
          delete([last_poll])
        new_poll = Locationpoll()
        new_poll.name = name
        event.location_polls.append(new_poll)
        save([self.user, event, new_poll])
        p1, p2 = self.event_attachment(event_hash, event)
        return [self.text_message(text="success!"), p1, p2]

    def cancel_location_edit(self):
        event_hash = self.user.is_editing_location
        if len(event_hash) == None:
          return [self.text_message("Ok canceled")]
        self.user.is_editing_location = ""
        save([self.user])
        p1, p2 = self.event_attachment(event_hash)
        return [self.text_message("Ok canceled"), p1, p2]

    def cancel_date_edit(self):
        add_time = self.user.is_adding_time
        remove_time = self.user.is_removing_time
        msgs = [self.text_message("Ok canceled")]
        self.user.is_adding_time = ""
        self.user.is_removing_time = ""
        save([self.user])
        event_hash = ""
        if len(add_time):
          msgs.extend(list(self.event_attachment(add_time)))
        elif len(remove_time):
          msgs.extend(list(self.event_attachment(remove_time)))
        return msgs

    def back_to_button(self, event_hash, event=None):
        if event == None:
            event = self.event_from_hash(event_hash)
        text = "Back to"
        title = "%s %s" % (CAL_EMOJI, str(event.title))
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
        self.clear_user()
        p1, p2 = self.event_attachment(event.event_hash, event)
        return [p1, p2]

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
        hrs = dateobj.strftime("%I")
        if ":" in hrs:
          start, end = hrs.split(":")
          end.replace("0", "")
          if len(end) == 1:
            end = "0" + end
          hrs = start + "-" + end
        datestr = dateobj.strftime("%a %m/%d @ ")
        datestr += hrs
        datestr += minute + ampm
        return datestr

    def current_user(self):
        return User.query.filter(User.messenger_uid==self.messenger_uid).first()

    def event_from_hash(self, event_hash):
        return Event.query.filter(Event.event_hash==event_hash).first()

    def capitalize_first_letter(self, words):
        for i in range(len(words)):
            words[i] = words[i][0].upper() + words[i][1:]
        return words

    def clear_user(self):
        self.user.is_editing_location = ""
        self.user.is_adding_time = ""
        self.user.is_removing_time = ""
        save([self.user])
