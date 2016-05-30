import requests
FB_GRAPH_URL = "https://graph.facebook.com/v2.6/"
MESNGR_API_URL = 'https://graph.facebook.com/v2.6/me/messages/?access_token='

def fetch_user_data(user_url, params):
  return requests.get(user_url, params=params).json()
