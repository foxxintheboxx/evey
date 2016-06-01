import requests
import random
FB_GRAPH_URL = "https://graph.facebook.com/v2.6/"
MESNGR_API_URL = 'https://graph.facebook.com/v2.6/me/messages/?access_token='
from config import TOKEN

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
