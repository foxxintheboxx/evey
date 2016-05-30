# -*- coding: utf-8 -*-
#IMG_ENDPOINTS

EXAMPLE_0 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/salsa.png?token=AE7-yjQHkXDtLhp_JYvc-5ceQCdM5lK0ks5XTRKmwA%3D%3D"
EXAMPLE_1 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/ee143.png?token=AE7-ylvIqLEZiA3FiGEzEz_uQBbbs5VWks5XTQvuwA%3D%3D"
EXAMPLE_2 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/fam.png?token=AE7-ytKht47y3ljQQgZZ6i4xwVMHzWNWks5XTRNVwA%3D%3D"

ABOUT_0 = "https://www.google.com/logos/2012/haring-12-hp.png"
ABOUT_1 = "https://s-media-cache-ak0.pinimg.com/736x/40/d4/7b/40d47b9ce63fae42b1ed196b11481bf6.jpg"

ONBOARDING_IMG_0 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/eventlink.png?token=AE7-yp9l5GadM4u2EOFbszkXYMdzODQUks5XUJKpwA%3D%3D"
ONBOARDING_IMG_1 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/coordinate.png?token=AE7-yg_eMyA8pggttSgr5GmkO3Y7iTacks5XUJLLwA%3D%3D"
ONBOARDING_IMG_2 = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/gettime.png?token=AE7-ymDdf4vWtFf_VgI-IzN-Ggtk9iZTks5XUJJ1wA%3D%3D"

CALENDAR_IMG = "https://raw.githubusercontent.com/foxxintheboxx/evey/master/app/static/onboarding_imgs/calendar_flat.png?token=AE7-ypni5exdUwg8vzql1r6zIn3B53Quks5XTSqBwA%3D%3D"

# FB_API_CONS
MSG_BODY = "message_body"
MSG_SUBJ = "message_subject"
LOCAL = "local_search_query"
DATE = "datetime"

#EMOJIS
WHEN_EMOJI = "🕐"
WHERE_EMOJI = "📍"
OTHER_EMOJI = "🔴"

# POSTBACKS
POSTBACK_TEMPLATE = "USER_PAYLOAD:%s"
SUBSCRIBE_POSTBACK = POSTBACK_TEMPLATE % "SUBSCRIBE:%s"
SHARE_POSTBACK = POSTBACK_TEMPLATE % "SHARE:%s"
WHEN_POSTBACK = POSTBACK_TEMPLATE % "WHEN:DATA:%s"
WHERE_POSTBACK = POSTBACK_TEMPLATE % "WHERE:DATA:%s"
OTHER_POSTBACK = POSTBACK_TEMPLATE % "OTHER:DATA:%s"

EVENT_POSTBACKS = {
  "subscribe": SUBSCRIBE_POSTBACK,
  "share": SHARE_POSTBACK,
  "where": WHERE_POSTBACK,
  "when": WHEN_POSTBACK,
  "other": OTHER_POSTBACK,
}


