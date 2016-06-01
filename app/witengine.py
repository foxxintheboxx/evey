import requests
from config import WIT_API


class WitEngine(object):

    def __init__(self, app_token, server_token,
                 content_type='application/json'):
        self.app_token = app_token
        self.server_token = server_token
        self.content_type = content_type

    def make_header(self, headers={}):
        default_header = {'Authorization': 'Bearer ' + self.server_token,
                          'Accept': 'application/json'}
        for key in headers.keys():
            default_header[key] = headers[key]
        return default_header

    def message(self, q, params={}, headers={}):
        query_url = WIT_API + "message"
        query_url += "?q=%s" % q
        query_url = self.__add_params__(params, query_url)
        headers = self.make_header(headers)
        return requests.get(query_url, headers=headers).json()

    def converse(self, session_id, q, params={}, headers={}):
        query_url = WIT_API + "converse"
        query_url += "?session_id=%s" % session_id
        if q is not None:
            query_url += "&q=%s" % q
        query_url = self.__add_params__(params, query_url)
        headers = self.make_header(headers)
        return requests.post(query_url, headers=headers).json()

    def __add_params__(self, params, query_url):
        for key in params.keys():
            query_url += "&%s=%s" % (key, self.remove_space(str(params[key])))
        return query_url

    def remove_space(self, query):
        return query.replace(' ', '%20')
