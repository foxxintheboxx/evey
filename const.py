# -*- coding: utf-8 -*-
#IMG_ENDPOINTS

EXAMPLE_0 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/ee143.png?token=AE7-yldtv6dfFOWxFHJ7Jf74kdVaOWRlks5XXfWOwA%3D%3D"
EXAMPLE_1 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/eventlink.png?token=AE7-yrfOEsrjZM-XK-PyFaCW2vyLsRrzks5XXfXZwA%3D%3D"
EXAMPLE_2 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/coordinate.png?token=AE7-yoywdgSU2kgaAAzdk73Ep6_rHBn7ks5XXfdDwA%3D%3D"

# FB_API_CONS
MSG_BODY = "message_body"
MSG_SUBJ = "message_subject"
LOCAL = "local_search_query"
DATE = "datetime"

# PARSING

DAY_ABRV = {"sun": "Sunday",
            "tues": "Tuesday",
            "tue": "Tuesday",
            "tu": "Tuesday",
            "th": "Thursday",
            "thu": "Thursday",
            "thur": "Thursday",
            "thurs": "Thursday",
            "wed": "Wednesday",
            "fri": "Friday",
            "sat": "Saturday",
            "mon": "Monday",}

#EMOJIS
WHEN_EMOJI = "🕐"
WHERE_EMOJI = "📍"
OTHER_EMOJI = "🔴"
GUY_EMOJI = "👦"
RED_A_EMOJI = ""
RED_X_EMOJI = "❌ "
PEOPLE_EMOJI = GUY_EMOJI + "👩"
PEOPLE_EMOJI = "👨‍👨‍👨"
GREEN_CHECK_EMOJI = "✅"
PAPER_EMOJI = "📎"
RIGHT_FINGER_EMOJI = "👉🏽"
KEY_EMOJI = "🔑"
CAL_EMOJI = "📅"
EMOJI_0 = "0️⃣"
EMOJI_1 = "1️⃣"
EMOJI_2 = "2️⃣"
EMOJI_3 = "3️⃣"
EMOJI_4 = "4️⃣"
EMOJI_5 = "5️⃣"
EMOJI_6 = "6️⃣"
EMOJI_7 = "7️⃣"
EMOJI_8 = "8️⃣"
EMOJI_9 = "9️⃣"
ELLIPSE = "🔸🔹🔸"

NUM = {
  0: EMOJI_0,
  1: EMOJI_1,
  2: EMOJI_2,
  3: EMOJI_3,
  4: EMOJI_4,
  5: EMOJI_5,
  6: EMOJI_6,
  7: EMOJI_7,
  8: EMOJI_8,
  9: EMOJI_9
}

EMOJI_NUM = dict((v,k) for k,v in NUM.iteritems())

DOWN_ARROW = "⬇️"
BLACK_CIRCLE = "●"
# FREQ USED
CANCEL = RED_X_EMOJI + " cancel"

# POSTBACKS
SUBSCRIBE_POSTBACK = "SUBSCRIBE"
SHARE_POSTBACK = "SHARE"
WHEN_POSTBACK = "WHEN"
WHERE_POSTBACK = "WHERE"
OTHER_POSTBACK = "OTHER"
WHO_POSTBACK = "WHO"
BACK_POSTBACK = "BACK"
CONFIRM_POSTBACK = "CONFIRM"
CANCEL_LOCATION_POSTBACK = "CANCEL_LOCATION"
CANCEL_EDIT = "CANCEL_EDIT"
CANCEL_REMOVE_TIME = "CANCEL_REMOVE_TIME"
ADD_TIME_POSTBACK = "ADD_TIME"
REMOVE_TIME_POSTBACK = "REMOVE_TIME"
MORE_TIMES_POSTBACK = "MORE_TIMES"
YES_EVENT_INVITE = "YES_EVENT_INVITE"
NO_EVENT_INVITE = "NO_EVENT_INVITE"

EVENT_POSTBACKS = {
  "subscribe": SUBSCRIBE_POSTBACK,
  "share": SHARE_POSTBACK,
  "where": WHERE_POSTBACK,
  "when": WHEN_POSTBACK,
  "who" : WHO_POSTBACK,
  "other": OTHER_POSTBACK,
  "back": BACK_POSTBACK,
  "add_time": ADD_TIME_POSTBACK,
  "remove_time": REMOVE_TIME_POSTBACK,
  "more_times": MORE_TIMES_POSTBACK,
  "cancel_edit": CANCEL_EDIT,
}

#  BASE URL
HEROKU_URL = "https://eveyai.herokuapp.com/"
EVEY_URL = "www.evey.ai/"

# COMMON MSGS
PLZ_SLOWDOWN = ("I'm sorry %s, but currently I am wayy better "
                "at understanding one request at a time. So "
                "plz only text me 1 thing at a time")
HELP = ("Hi %s! this is how to use me!\n"
        "> 'make' <event name> \n"
        "> 'find' <event name>\n"
        "> 'events' to see all your events")


