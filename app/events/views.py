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
           " heres the event's details")


@events.route('/<event_id>', methods=['GET'])
@login_required
def access_event(event_id):
    print("accessed event" + event_id)
    messenger_uid = current_user.messenger_uid
    user = db.session.query(User).filter((User.messenger_uid==messenger_uid)).first()
    event = Event.query.filter(Event.event_hash==event_id).first()
    print(user.timezone)
    print(user)
    if event is None:
        return render_template("404.html")
    title = event.title
    evey = EveyEngine(current_user.first_name, user, messenger_uid)
    event.calendars.append(current_user.calendar)

    db.session.add(event)
    db.session.commit()

    print(event)
    pkt0 = evey.event_attachment(event.event_hash, event=event)

    msgs = [evey.text_message(WELCOME % (current_user.first_name, title)), pkt0]
    for msg in msgs:
        payload = {'recipient': {'id': messenger_uid}, 'message': msg}
        r = requests.post(MESNGR_API_URL + TOKEN, json=payload)
        print(r)
    return render_template("event.html",
                           title=title,
                           user=current_user)
