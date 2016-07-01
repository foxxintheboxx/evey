import requests
import random
import re
import json
from datetime import timedelta, datetime
from . import db


FB_GRAPH_URL = "https://graph.facebook.com/v2.6/"
MESNGR_API_URL = 'https://graph.facebook.com/v2.6/me/messages/?access_token='
from config import TOKEN
import const as c

user_details_params = {'fields': 'first_name,last_name,profile_pic,timezone',
                       'access_token': TOKEN}


def fetch_user_data(user_url, params=user_details_params):
    return requests.get(FB_GRAPH_URL + user_url, params=params).json()


def generate_hash():
    alpha = 'abcdefghijklmnop'
    possibles = ('0123456789'
                 + alpha.upper()
                 + alpha.lower())
    return ''.join(random.choice(possibles) for i in range(5))


def format_ampm(string):
    opp = {"am": "pm", "pm": "am"}
    string = string.lower()
    start, end = string.split("-")
    start_val = int(re.search("\d\d?", start).group(0))
    end_val = int(re.search("\d\d?", end).group(0))

    start_zone = None
    end_zone = None
    if ("pm" in start):
        start_zone = "pm"
    if ("am" in start):
        start_zone = "am"
    if ("pm" in end):
        end_zone = "pm"
    if ("am" in end):
        end_zone = "am"
    else:
        end_zone = "pm"
    if start_zone is None and start_val < end_val:
        start_zone = end_zone
    elif start_zone is None:
        start_zone = opp[end_zone]
    elif end_zone is None and start_val < end_val:
        end_zone = start_zone
    elif end_zone is None:
        end_zone = opp[start_zone]
    return "%s%s-%s%s" % (start_val, start_zone, end_val, end_zone)


def string_to_day(string):
    fullnames = c.DAY_ABRV.values()
    if string in fullnames:
        return string
    return c.DAY_ABRV.get(string.lower())


def encode_unicode(unicode_string):
    return unicode_string.encode("utf-8")


def save(models):
    print("saving")
    print(models)
    models = set(models)
    for model in models:
        db.session.add(model)
    db.session.commit()


def delete(models):
    print("deleting")
    print(models)
    models = set(models)
    for model in models:
        db.session.delete(model)
    db.session.commit()


def format_postback(postback, data_dict):
    return postback + "$" + json.dumps(data_dict)


def format_event_postbacks(postbacks, event_hash):
    postbacks = dict(postbacks)
    for key in postbacks.keys():
        event_data = {"event_hash": event_hash}
        postbacks[key] = format_postback(postbacks[key], event_data)
    return postbacks


def format_dateobj(dateobj, to_dateobj=None, offset=0, use_day=True,
                   use_at=True):
    today = datetime.utcnow()
    ampm = "am"
    dateobj = (dateobj + timedelta(hours=offset))
    if dateobj.hour % 24 > 12:
        ampm = "pm"
    minute = ""
    if dateobj.minute > 0:
        minutes = str(dateobj.minute)
        if len(minutes) < 2:
            minutes = "0" + minutes
        minute = ":" + minutes
    hrs = dateobj.strftime("%I")
    if hrs != "10":
        hrs = hrs.replace("0", "")
    to_hrs = ""
    to_minute = ""
    if to_dateobj:
        to_dateobj = (to_dateobj + timedelta(hours=offset))
        to_hrs = to_dateobj.strftime("%I")
        if to_hrs != "10":
            to_hrs = to_hrs.replace("0", "")
        if to_dateobj.minute > 0:
            minutes = str(to_dateobj.minute)
            if len(minutes) < 2:
                to_minutes = "0" + minutes
            to_minute = ":" + to_minutes
    if ":" in hrs:
        start, end = hrs.split(":")
        end.replace("0", "")
        if len(end) == 1:
            end = "0" + end
        hrs = start + "-" + end
    month = dateobj.strftime("%m")
    day = dateobj.strftime("%d")
    if month != "10":
        month = month.replace("0", "")
    if day not in ["10", "20", "30"]:
        day = day.replace("0", "")
    datestr = ""
    if use_day:
        day_name = dateobj.strftime("%a")
        datestr = "%s %s/%s " % (day_name, month, day)
        if (dateobj.day == today.day and dateobj.month == today.month):
            datestr = "Today "
    if use_at:
        datestr = datestr + "@ "

    datestr += hrs
    datestr += minute
    if len(to_hrs) > 0:
        datestr += "-" + to_hrs + to_minute  # TODO
    datestr += ampm
    return datestr


def numbers_from_tokens(str_tokens):
    numbers = []
    for t in str_tokens:
        try:
            t = t.encode("utf-8")
            value = c.EMOJI_NUM.get(t)
            if value:
                numbers.append(value)
            else:
                numbers.append(int(t))
        except:
            continue
    return numbers


def number_to_emojistr(number):
    i = 10
    emojistr = ""
    while (len(emojistr) == 0 or (number) > 0):
        digit = number % i
        emojistr = c.NUM[digit] + emojistr
        number /= i
    return emojistr


def event_times_text(event, timezone=0, user=None, length=5, show_title=False):
    date_polls = event.get_datepolls()
    now = datetime.utcnow()
    text = ""
    if show_title:
        text = "%s %s by %s" % (c.CAL_EMOJI, str(event.title), str(event.creator.first_name))
    if user is not None:
        text = "Here is your %ss:\n" % c.WHEN_EMOJI
    if len(date_polls) == 0:
        text = "Looks like no one has added any of their availabilities yet\n"
    else:
        prev_date = ""
        for poll in date_polls:
            if poll.poll_number == 2 and user is None:
                text += "-" * min(len(text), 9) + "\n"
            if user is not None and user not in poll.users:
                continue
            votes = ""
            if poll.votes() > 2:
                votes = "%sx%s" % (poll.votes(), c.GUY_EMOJI)
            else:
                votes = c.GUY_EMOJI * poll.votes()
            dateobj = poll.datetime + timedelta(hours=timezone)
            indent = "      "
            date = dateobj.strftime("%a %m/%d")
            if (dateobj.day == now.day and dateobj.month == now.month):
                date = "Today"
            if prev_date != date:
                text += date + "\n"
                prev_date = date

            date_str = format_dateobj(poll.datetime, poll.end_datetime,
                                      timezone, use_day=False,
                                      use_at=False)
            text += "%s%s %s, %s\n" % (indent,
                                       number_to_emojistr(
                                           poll.poll_number),
                                       date_str,
                                       votes)
            length -= 1
            if length == 0:
                break
    return text
