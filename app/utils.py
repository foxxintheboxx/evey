import requests
import random
import re

FB_GRAPH_URL = "https://graph.facebook.com/v2.6/"
MESNGR_API_URL = 'https://graph.facebook.com/v2.6/me/messages/?access_token='
from config import TOKEN
from const import DAY_ABRV

user_details_params =  {'fields':'first_name,last_name,profile_pic',
                        'access_token':TOKEN}

def fetch_user_data(user_url, params=user_details_params):
  return requests.get(FB_GRAPH_URL + user_url, params=params).json()


def generate_hash():
  alpha = 'abcdefghijklmnop'
  possibles = ('0123456789'
               + alpha.upper()
               + alpha.lower())
  return ''.join(random.choice(possibles) for i in range(10))

def format_ampm(string):
  opp = {"am":"pm", "pm":"am"}
  string = string.lower()
  start, end  = string.split("-")
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
  if start_zone == None and start_val < end_val:
    start_zone = end_zone
  elif start_zone == None:
    start_zone = opp[end_zone]
  elif end_zone == None and start_val < end_val:
    end_zone = start_zone
  elif end_zone == None:
    end_zone = opp[start_zone]
  return "%s%s-%s%s" % (start_val, start_zone, end_val, end_zone)

def string_to_day(string):
  fullnames = DAY_ABRV.values()
  if string in fullnames:
    return string
  return DAY_ABRV.get(string.lower())
