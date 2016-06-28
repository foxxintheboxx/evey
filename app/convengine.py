from dateutil.parser import parse
from dateutil.tz import tzutc
import json
from datetime import timedelta
from .witengine import WitEngine
from .fbapimethods import FBAPI
from .models import User, Event, Datepoll, Locationpoll
from .utils import fetch_user_data, save, delete, encode_unicode, \
     format_dateobj, format_event_postbacks, format_postback, \
     numbers_from_tokens, generate_hash, number_to_emojistr, event_times_text
from config import WIT_APP_ID, WIT_SERVER
from .onboardengine import OnboardEngine
from const import WHEN_EMOJI, WHERE_EMOJI, OTHER_EMOJI, EVEY_URL, MSG_BODY, \
    MSG_SUBJ, LOCAL, DATE, EVENT_POSTBACKS, GUY_EMOJI, CONFIRM_POSTBACK, \
    ADD_TIME_POSTBACK, REMOVE_TIME_POSTBACK, NUM, CAL_EMOJI, RED_X_EMOJI, CANCEL, DOWN_ARROW, \
    BLACK_CIRCLE, EMOJI_NUM, PAPER_EMOJI, RIGHT_FINGER_EMOJI, PLZ_SLOWDOWN, \
    YES_EVENT_INVITE, NO_EVENT_INVITE, KEY_EMOJI, GREEN_CHECK_EMOJI


class EveyEngine(WitEngine, FBAPI):

    def __init__(self, first_name, user, messenger_uid):
        super(EveyEngine, self).__init__(WIT_APP_ID, WIT_SERVER)
        self.user_name = first_name
        self.messenger_uid = messenger_uid
        self.user = user
        self.onboarder = OnboardEngine(first_name, user, messenger_uid)
        self.postback_func = {
            EVENT_POSTBACKS["share"]: self.get_event_link,
            EVENT_POSTBACKS["who"]: self.see_people_in_event,
            EVENT_POSTBACKS["back"]: self.back_to_callback,
            EVENT_POSTBACKS["when"]: self.collab_date_callback,
            EVENT_POSTBACKS["where"]: self.edit_location,
            EVENT_POSTBACKS["add_time"]: self.add_date_callback,
            EVENT_POSTBACKS["remove_time"]: self.remove_date_callback,
            EVENT_POSTBACKS["more_times"]: self.show_all_times,
            EVENT_POSTBACKS["cancel_edit"]: self.cancel_edit,
            CONFIRM_POSTBACK: self.confirm_location_change,
            YES_EVENT_INVITE: self.ask_for_event_msg,
            NO_EVENT_INVITE: self.show_tutorial,
            }

    def understand(self, msgs):
        if len(msgs) == 0:
            return []
        if len(msgs) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        if msgs[0].lower() == "help":
            return self.onboarder.onboarding_1()
        event = self.parse_event_msg(msgs[0])
        if event != None:
            return [self.event_attachment(event.event_hash, event)]
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

    def parse_event_msg(self, msg):
        tokens = [token.split(" ") for token in  msg.splitlines()]
        tokens = [t for ts in tokens for t in ts]
        event = None
        for token in tokens:
            token = token.replace("#", "")
            if len(token) == 5:
                event = self.event_from_hash(token)
                if event != None:
                    event.calendars.append(self.user.calendar)
                    save([event])
                    break
        return event

    def determine_response(self, msg_data):
        entities = msg_data["entities"]
        if "event" not in entities:
            return [self.onboarder.onboarding_1()[0]]
        if (entities.get("message_body") is None and
                entities.get("message_subject") is None):
            return [self.text_message("What do you wanna call the event?")]
        event = self.create_event(entities)
        p1 = self.event_attachment(event.event_hash, event=event)
        return [p1]

    def create_event(self, entities):
        title = entities.get(MSG_SUBJ)
        if title is None:
            title = entities.get(MSG_BODY)
        title = title[0]["value"]
        title_words = self.capitalize_first_letter(title.split(" "))
        title = " ".join(title_words)
        curr_user = self.user
        calendar = curr_user.calendar
        event = Event(title=title)
        event.event_hash = generate_hash()
        calendar.events.append(event)
        objects = [event, calendar]
        if DATE in entities:
            dateobj = parse(entities[DATE][0]["value"]).astimezone(tzutc())
            datepoll = Datepoll(datetime=dateobj)
            datepoll.users.append(curr_user)
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
        if event is None:
            event = self.event_from_hash(event_hash)

        title = "%s %s" % (CAL_EMOJI, str(event.title))
        postbacks = format_event_postbacks(EVENT_POSTBACKS,
                                           event.event_hash)
        date_exists = False
        top_date = event.get_top_date()
        attendees = len(event.attendees())
        date = ""
        if top_date is not None:
            dateobj = top_date.datetime
            votes = top_date.votes()
            date_str = format_dateobj(dateobj, top_date.end_datetime,
                                      self.user.timezone)
            date = "%s %s" % (WHEN_EMOJI, date_str)
        else:
            date = "%s none yet" % (WHEN_EMOJI)

        top_location = event.get_top_local()
        where = ""
        if top_location is not None:
            where_str = str(top_location.name)
            where = "%s %s" % (WHERE_EMOJI, where_str)
        else:
            where = "%s none yet" % (WHERE_EMOJI)
        people = GUY_EMOJI * attendees

        if attendees > 3:
            people = "%sx%s" % (GUY_EMOJI, attendees)
        buttons_msg0 = [self.make_button("postback", date,
                                         postbacks["when"]),
                        self.make_button("postback", people,
                                         postbacks["who"]),
                        self.make_button("postback", "invite ppl to this",
                                         postbacks["share"])]
        msg_elements0 = [self.make_generic_element(title=title,
                                                   buttons=buttons_msg0)]
        evey_resp = self.generic_attachment(msg_elements0)
        return evey_resp

    def ask_for_event_msg(self):
        return [self.text_message(("Great, just paste the msg and send it to me!\n"
                                    "(P.s. Any future event msgs you can paste to me also!)"))]

    def show_tutorial(self):
        return self.onboarder.onboarding_1()

    def get_event_link(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        title = str(event.title)
        key = str(event.event_hash)
        text = "txt this %s #%s to evey @ m.me/evey.io to unlock \"%s\"" % (KEY_EMOJI, key, title)
        text += "(save time & paste this entire msg to her)"
        return [self.text_message("forward this msg" + DOWN_ARROW),
                self.text_message(text)]

    def see_people_in_event(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        calendars = event.calendars
        ppl_attachments = []
        attendees =  event.attendees()
        for i in range(len(attendees)):
            person = attendees[i]
            messenger_uid = person.messenger_uid
            user_data = fetch_user_data(messenger_uid)
            buttons =  []
            buttons = [self.back_to_button(event.event_hash, event)]
            el = self.make_generic_element(title=person.name,
                                           img_url=user_data["profile_pic"],
                                           buttons=[])
            ppl_attachments.append(el)
        return [self.generic_attachment(ppl_attachments)]


    def handle_postback(self, keys):
        if len(keys) > 1:
            return [self.text_message(PLZ_SLOWDOWN % self.user_name)]
        postback_data = str(keys[0]).split('$')
        if len(postback_data) > 1:
            data = json.loads(postback_data[1])
            return self.postback_func[postback_data[0]](data)
        return self.postback_func[postback_data[0]]()

    def handle_add_time(self, msg):
        event = self.event_from_hash(self.user.is_adding_time)
        intervals = self.extract_intervals(msg)
        tokens = msg.split(" ")
        tokens = [encode_unicode(el.replace(",", "")) for el in tokens]
        numbers =  numbers_from_tokens(tokens)
        for i in intervals:
            event.add_new_interval(i.get("from"), i.get("to"), self.user)
        datepolls = event.get_datepolls()
        for n in set(numbers):
            if n > len(datepolls) or n < 1:
                continue  # add some degradation
            datepolls[n - 1].users.append(self.user)
        save(event.get_datepolls())
        save([self.user, event])
        text = GREEN_CHECK_EMOJI + " I added your times!"
        text2 = event_times_text(event, self.user.timezone)
        return [self.text_message(text),
                self.button_attachment(
                    text=text2, buttons=[self.back_to_button(event.event_hash,
                                                             event)])]

    def handle_remove_time(self, msg):
        event = self.event_from_hash(self.user.is_removing_time)
        intervals = self.extract_intervals(msg)
        tokens = msg.split(" ")
        tokens = [encode_unicode(el.replace(",", "")) for el in tokens]
        numbers =  numbers_from_tokens(tokens)
        for i in intervals:
            event.remove_interval(i.get("from"), i.get("to"), self.user)
        datepolls = event.get_datepolls()
        for n in set(numbers):
            if n > len(datepolls) or n < 1:
                continue  # add some degradation
            datepolls[n - 1].users.append(self.user)

        save(event.get_datepolls())
        save([self.user, event])
        text = GREEN_CHECK_EMOJI + " I removed your times!"
        text2 = event_times_text(event, self.user.timezone)
        return [self.text_message(text),
                self.button_attachment(
                    text=text2, buttons=[self.back_to_button(event.event_hash,
                                                             event)])]

    def collab_date_callback(self, event_json, length=5):
        event = self.event_from_hash(event_json["event_hash"])
        text = event_times_text(event, self.user.timezone, length=length)
        postbacks = format_event_postbacks(dict(EVENT_POSTBACKS),
                                           event.event_hash)
        buttons = []
        num_polls = len(event.get_datepolls())
        if num_polls > length:
            diff = num_polls - length
            more_button = self.make_button(
                type_="postback", title=("+%s more %ss" % (diff, WHEN_EMOJI)),
                payload=postbacks["more_times"])
            buttons.append(more_button)

        add_button = self.make_button(
            type_="postback",
            title="add " + WHEN_EMOJI,
            payload=postbacks["add_time"])

        buttons.append(add_button)
        remove_button = self.make_button(
            type_="postback",
            title="remove " + WHEN_EMOJI,
            payload=postbacks["remove_time"])
        if event.user_has_voted(self.user):
            buttons.append(remove_button)

        save([self.user])
        back_button = self.make_button(type_="postback", title=CANCEL,
                                       payload=postbacks["cancel_edit"])
        buttons.append(back_button)
        return [self.button_attachment(text=text, buttons=buttons)]

    def add_date_callback(self, event_json):
        self.user.is_adding_time = event_json["event_hash"]
        save([self.user])
        event = self.event_from_hash(event_json["event_hash"])
        number_dialog = (BLACK_CIRCLE + " text me a number i.e." +
                          NUM[1] + ", " + NUM[2] + "\n")
        reg_dialog = (BLACK_CIRCLE + " or, a new time i.e. Thu 3-4pm")
        text1 = ("To add your " + WHEN_EMOJI + " :\n")
        if len(event.get_datepolls()):
          text1 += number_dialog
        text1 += reg_dialog
        postbacks = format_event_postbacks(dict(EVENT_POSTBACKS),
                                           event.event_hash)
        buttons = []
        back_button = self.make_button(
            type_="postback", title="%s %s" %
            (CAL_EMOJI, str(event.title)), payload=postbacks["cancel_edit"])
        buttons.append(back_button)
        return [self.button_attachment(text=text1, buttons=buttons)]

    def show_all_times(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        length = len(event.get_datepolls())
        return self.collab_date_callback(event_json, length=length)

    def remove_date_callback(self, event_json):
        self.user.is_removing_time = event_json["event_hash"]
        self.user.is_adding_time = ""
        save([self.user])
        event = self.event_from_hash(event_json["event_hash"])
        num_polls = len(event.get_datepolls())
        text = event_times_text(event, self.user.timezone, user=self.user, length=num_polls)
        buttons = []
        text1 = ("To remove your " + WHEN_EMOJI + " :\n" +
                 BLACK_CIRCLE + " text me a number i.e." +
                 NUM[1] + ", " + NUM[2] + "\n" +
                 BLACK_CIRCLE + " or, a new time i.e. Thu 3-4pm")
        postbacks = format_event_postbacks(dict(EVENT_POSTBACKS),
                                           event.event_hash)
        back_button = self.make_button(
            type_="postback", title="%s %s" %
            (CAL_EMOJI, str(event.title)), payload=postbacks["cancel_edit"])
        buttons.append(back_button)
        return [self.text_message(text),
                self.button_attachment(text=text1, buttons=buttons)]

    def edit_location(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        location_poll = event.location_polls.first()
        text = "Text me a new " + WHERE_EMOJI + ". Or, press " + RED_X_EMOJI
        self.user.is_editing_location = event.event_hash
        save([self.user])
        postbacks = format_event_postbacks(dict(EVENT_POSTBACKS),
                                           event.event_hash)
        cancel_button = self.make_button(type_="postback", title=CANCEL,
                                         payload=postbacks["cancel_edit"])
        return [self.button_attachment(text=text, buttons=[cancel_button])]

    def handle_edit_location(self, msg):
        words = self.capitalize_first_letter(msg.split(" "))
        location = " ".join(words)
        text = "Is this correct? %s" % location
        confirm_postback = format_postback(CONFIRM_POSTBACK,
                                           {"name": location})
        confirm_button = self.make_button(type_="postback", title="Yes",
                                          payload=confirm_postback)
        cancel_button = self.make_button(type_="postback", title="cancel",
                                         payload=postbacks["cancel_edit"])
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
        p1 = self.event_attachment(event_hash, event)
        return [self.text_message(text="success!"), p1]

    def cancel_edit(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        msgs = [self.text_message("Ok canceled")]
        self.clear_user()
        event_hash = ""
        msgs.append(self.event_attachment(event.event_hash, event))
        return msgs

    def back_to_button(self, event_hash, event=None):
        if event is None:
            event = self.event_from_hash(event_hash)
        text = "Back to"
        title = "%s %s" % (CAL_EMOJI, str(event.title))
        if len(event.title) > 20:
            title = title[:17] + "..."
        postbacks = format_event_postbacks(dict(EVENT_POSTBACKS),
                                           event.event_hash)
        back_button = self.make_button(type_="postback", title=title,
                                       payload=postbacks["back"])
        return  back_button

    def back_to_callback(self, event_json):
        event = self.event_from_hash(event_json["event_hash"])
        self.clear_user()
        return [self.event_attachment(event.event_hash, event)]

    def event_from_hash(self, event_hash):
        return Event.query.filter(Event.event_hash == event_hash).first()

    def capitalize_first_letter(self, words):
        for i in range(len(words)):
            words[i] = words[i][0].upper() + words[i][1:]
        return words

    def clear_user(self):
        self.user.is_editing_location = ""
        self.user.is_adding_time = ""
        self.user.is_removing_time = ""
        save([self.user])
