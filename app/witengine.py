import requests
from dateutil.parser import parse
from dateutil.tz import *
from config import WIT_API
from datetime import timedelta, datetime
import re
from .utils import format_ampm, string_to_day
from const import DATE

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

    def extract_intervals(self, msg, look_ahead=2):
        tokens = msg.split(" ")
        tokens  = [el.replace(",", "") for el in tokens]
        pattern_interval  = "\d\d?:?\d?\d?[APap]?[mM]?-\d\d?:?\d?\d?[APap]?[mM]?"
        matches = re.findall(pattern_interval, msg)
        intervals = []
        if len(matches) > 0:
            for i in range(len(matches)):
                match = matches[i]
                j = tokens.index(match)
                m = format_ampm(match)
                day = None
                if j > 0:
                    string = tokens[j - 1]
                    day = string_to_day(string)
                if not day and j > 1:
                    string = tokens[j - 2]
                    day = string_to_day(string)
                if not day:
                    day = "Today"
                start_time, end_time = m.split("-")
                query = "%s %s to %s %s" % (day, start_time, day, end_time)
                wit_resp = self.message(query)["entities"][DATE][0]
                from_ = parse(wit_resp["from"]["value"]).astimezone(tzutc())
                to =  parse(wit_resp["to"]["value"]).astimezone(tzutc())
                to = to - timedelta(hours = 1)
                interval = {"from": from_, "to": to}
                print(interval)
                intervals.append(interval)
                tokens.remove(match)
        pattern_single = "\d\d?:?\d?\d?[APap]?[mM]?"
        matches = re.findall(pattern_single, msg)
        if len(matches) > 0 and len(intervals) == 0:
            for i in range(len(matches)):
                match = matches[i]
                if (match not in tokens):
                    continue
                j = tokens.index(match)
                m = match
                if ("m" not in m):
                    m = match + "pm"
                day = None
                if j > 0:
                    string = tokens[j - 1]
                    day = string_to_day(string)
                if not day and j > 1:
                    string = tokens[j - 2]
                    day = string_to_day(string)
                if not day:
                    day = "Today"
                start_time = m
                query = "%s %s"  % (day, start_time)
                wit_resp = self.message(query)["entities"][DATE][0]
                from_ = parse(wit_resp["value"]).astimezone(tzutc())
                interval = {"from": from_, "to": None}
                print(interval)
                intervals.append(interval)
                tokens.remove(match)
                match = matches[i]

        if len(intervals) == 0:
            wit_resp = self.message(msg)["entities"]
            if wit_resp.get(DATE):
                data = wit_resp.get(DATE)
                for obj in data:
                    if obj.get("type") == "value":
                        intervals.append(
                            {"from": parse(obj.get("value")).astimezone(tzutc())})
                    if obj.get("type") == "interval":
                        from_ = parse(obj["from"]["value"]).astimezone(tzutc())
                        to =  parse(obj["to"]["value"]).astimezone(tzutc())
                        to = to - timedelta(hours = 1)
                        interval = {"from": from_, "to": to}
                        intervals.append(interval)
        return intervals

