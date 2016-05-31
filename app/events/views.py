from flask import render_template
from flask.ext.login import login_required, current_user
from ..utils import MESNGR_API_URL
from config import TOKEN

from . import events
from .. import db
from ..models import User, Event
from ..convengine import EveyEngine
import requests


WELCOME = ("Hey %s, thanks for accessing %s!"
           "heres the event's details")


@events.route('/events/<event_id>', methods=['GET'])
@login_required
def access_event(event_id):
    print("accessed event" + event_id)
    messenger_uid = current_user.messenger_uid
    event = Event.query.filter(Event.event_hash==event_id).first()

    if event is None:
        return render_template("404.html")
    title = event.title
    msg = EveyEngine(current_user.first_name, current_user,
                     messenger_uid).text_message(WELCOME % (current_user.first_name,
                                                            title))
    payload = {'recipient': {'id': messenger_uid}, 'message': msg}
    r = requests.post(MESNGR_API_URL + TOKEN, json=payload)
    print(r)
    return render_template("event.html",
                           title=title,
                           user=current_user)
