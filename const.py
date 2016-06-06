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

#EMOJIS
WHEN_EMOJI = "🕐"
WHERE_EMOJI = "📍"
OTHER_EMOJI = "🔴"
GUY_EMOJI = "👦"
PEOPLE_EMOJI = GUY_EMOJI + "👩"

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

EVENT_POSTBACKS = {
  "subscribe": SUBSCRIBE_POSTBACK,
  "share": SHARE_POSTBACK,
  "where": WHERE_POSTBACK,
  "when": WHEN_POSTBACK,
  "who" : WHO_POSTBACK,
  "other": OTHER_POSTBACK,
  "back": BACK_POSTBACK
}

#  BASE URL
EVEY_URL = "https://eveyai.herokuapp.com/"
