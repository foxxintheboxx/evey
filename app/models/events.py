from .. import db
from datetime import datetime
from ..utils import save, delete
from .datepolls import Datepoll

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    event_hash = db.Column(db.String, unique=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendar.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    datetime = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    title = db.Column(db.String(64))
    location_polls = db.relationship('Locationpoll',
                                     backref='event',
                                     lazy='dynamic')
    date_polls = db.relationship('Datepoll',
                                 backref='event',
                                 lazy='dynamic')

    def __repr__(self):
        return '<Event %r>' % self.title

    def get_top_poll(self, poll):
        votes = -1
        top_p = None
        for p in poll:
            if p.votes() > votes:
                top_p = p
                votes = p.votes()
        return top_p

    def get_top_date(self):
        return self.get_top_poll(self.date_polls)

    def get_top_local(self):
        return self.get_top_poll(self.location_polls)

    def user_added_time(self, user):
        for p in self.date_polls:
            for u in p.users:
                if u.messenger_uid == user.messenger_uid:
                    return True
        return False

    def append_datepoll(self, poll):
        if poll.datetime == None:
            return
        self.date_polls.append(poll)
        poll.poll_number = len(self.date_polls.all())

    def attendees(self):
        return [cal.user for cal in self.calendars]

    def sort_datepolls(self, datepoll_list):
        datepoll_list.sort(key=lambda x: x.votes(), reverse=True)
        if (len(datepoll_list) ==  0):
            return
        first_poll = datepoll_list[0]
        first_poll.poll_number = 1
        datepoll_list.remove(first_poll)
        datepoll_list.sort(key=lambda x: x.datetime)
        for i in range(len(datepoll_list)):
            datepoll_list[i].poll_number = i + 2
        datepoll_list.insert(0, first_poll)

    def get_datepolls(self):
        datepoll_list = self.date_polls.all()
        self.sort_datepolls(datepoll_list)
        return datepoll_list

    def user_has_voted(self, user):
        datepolls = self.get_datepolls()
        for p in datepolls:
            if user in p.users:
                return True
        return False

    def add_new_interval(self, from_dateobj, to_dateobj, user):
        date_polls = self.get_datepolls()
        intersecting_polls = []
        old_polls = []
        for poll in date_polls:
            if ((poll.end_datetime is None and to_dateobj is not None) or
                (to_dateobj is None and poll.end_datetime is not None)):
                continue
            if (poll.datetime == from_dateobj and
                poll.end_datetime is None and to_dateobj is None):
                poll.add_users([user])
                intersecting_polls.append(poll)
                break
            if (to_dateobj is None):
                break
            if (to_dateobj <= poll.datetime or from_dateobj >= poll.end_datetime):
                continue
            time0, time1, time2, time3 = self.__interval_times(
                from_dateobj, to_dateobj, poll)
            inner_interval = None
            outer_interval = None
            users = poll.users
            if (time0 == time1 and time2 == time3):
                poll.add_users([user])
                intersecting_polls.append(poll)
                break
            elif (time0 == time1 and time2 < time3):  # 1
                inner_interval = Datepoll(datetime=time0, end_datetime=time2)
                outer_interval = Datepoll(datetime=time2, end_datetime=time3)
                inner_interval.add_users(users + [user])
                if (time2 == to_dateobj):
                    outer_interval.add_users(users)
                else:
                    outer_interval.add_users([user])
            elif (time0 < time1 and time2 == time3):  # 2
                outer_interval = Datepoll(datetime=time0, end_datetime=time1)
                inner_interval = Datepoll(datetime=time1, end_datetime=time3)
                inner_interval.add_users([user] + users)
                if (time0 == from_dateobj):
                    outer_interval.add_users([user])
                else:
                    outer_interval.add_users(users)
            else:
                first_outer_interval = Datepoll(
                    datetime=time0, end_datetime=time1)
                inner_interval = Datepoll(datetime=time1, end_datetime=time2)
                outer_interval = Datepoll(datetime=time2, end_datetime=time3)
                intersecting_polls.append(first_outer_interval)
                inner_interval.add_users([user] + users)
                if (time0 == from_dateobj):
                    first_outer_interval.add_users([user])
                    if (time2 == to_dateobj):
                        outer_interval.add_users(users)
                    else:
                        outer_interval.add_users([user])
                else:
                    first_outer_interval.add_users(users)
                    if (time2 == to_dateobj):
                        outer_interval.add_users(users)
                    else:
                        outer_interval.add_users([user])
            intersecting_polls.extend([inner_interval, outer_interval])
            old_polls.append(poll)
        if len(intersecting_polls) == 0:
            poll = Datepoll(datetime=from_dateobj, end_datetime=to_dateobj)
            poll.add_users([user])
            intersecting_polls.append(poll)
        for poll in intersecting_polls:
            self.append_datepoll(poll)
        print(intersecting_polls)

        save(intersecting_polls)
        delete(old_polls)
        self.merge_polls()
        return intersecting_polls

    def merge_polls(self):
        datepoll_list = self.date_polls.all()
        datepoll_list.sort(key=lambda x: x.datetime)
        datepoll_list = filter(lambda x: x.end_datetime is not None,
                               datepoll_list)
        polls_to_merge= []
        curr_poll_group = []
        used_prev = False
        for i in range(len(datepoll_list)):
            if i == 0:
                continue
            curr = datepoll_list[i]
            prev = datepoll_list[i - 1]
            print(self.has_same_users(curr, prev))
            if (curr.datetime <= prev.end_datetime
                and self.has_same_users(curr, prev)):
                if used_prev == False:
                    used_prev = True
                    curr_poll_group = [prev]
                    polls_to_merge.append(curr_poll_group)
                curr_poll_group.append(curr)
            else:
                used_prev = False
        polls_to_delete = []
        polls_to_save = []
        print(polls_to_merge)
        for group in polls_to_merge:
            begin = group[0]
            end = group[len(group) - 1]
            new_poll = Datepoll(datetime=begin.datetime, end_datetime=end.end_datetime)
            new_poll.users = begin.users
            polls_to_save.append(new_poll)
            polls_to_delete.extend(group)
        delete(polls_to_delete)
        for poll in polls_to_save:
            self.append_datepoll(poll)

        save(polls_to_save)


    def has_same_users(self, poll1, poll2):
        return set(poll1.users) == set(poll2.users)

    def remove_interval(self, from_dateobj, to_dateobj, user):
        polls = self.get_datepolls()
        old_polls = []
        new_polls = []
        updated_polls = []
        for p in polls:
            print(user not in p.users)
            if user not in p.users:
                continue
            if (p.end_datetime is None and to_dateobj is None and from_dateobj == p.datetime):
                new_users = p.users
                new_users.remove(user)
                p.users = new_users
                if (len(p.users) == 0):
                    old_polls.append(p)
                else:
                    updated_polls.append(p)
                break

            if (p.end_datetime is None and to_dateobj is not None):
                if ((from_dateobj == p.datetime or to_dateobj == p.datetime) or
                     (from_dateobj < p.datetime and p.datetime < to_dateobj)):
                    new_users = p.users
                    new_users.remove(user)
                    p.users = new_users
                    if (len(p.users) == 0):
                        old_polls.append(p)
                    else:
                        updated_polls.append(p)
                break


            if ((to_dateobj is None and p.end_datetime is not None) or (from_dateobj > p.end_datetime) or (to_dateobj < p.datetime)):
                continue
            if (poll.datetime == from_dateobj and
                poll.end_datetime is None and to_dateobj is None):
                poll.add_users([user])
                intersecting_polls.append(poll)
                break
            print(p.datetime)
            print(p.end_datetime)
            if (from_dateobj <= p.datetime and to_dateobj >= p.end_datetime):
                new_users = p.users
                new_users.remove(user)
                p.users = new_users
                if (len(p.users) == 0):
                    old_polls.append(p)
                else:
                    updated_polls.append(p)
            if (from_dateobj <= p.datetime and to_dateobj < p.end_datetime):
                poll_with_user = Datepoll(datetime=to_dateobj,
                                          end_datetime=p.end_datetime)
                new_polls.append(poll_with_user)
                poll_with_user.users = p.users
                new_users = p.users
                new_users.remove(user)
                old_polls.append(p)
                if (len(new_users) != 0):
                    poll_wo_user = Datepoll(datetime=p.datetime, end_datetime=to_dateobj)
                    poll_wo_user.users = new_users
                    new_polls.append(poll_wo_user)
            elif (from_dateobj > p.datetime and to_dateobj > p.end_datetime):
                poll_with_user = Datepoll(datetime=p.datetime,
                                          end_datetime=from_dateobj)
                new_polls.append(poll_with_user)
                poll_with_user.users = p.users
                new_users = p.users
                new_users.remove(user)
                old_polls.append(p)
                if (len(new_users) != 0):
                    poll_wo_user = Datepoll(datetime=from_dateobj, end_datetime=p.end_datetime)
                    poll_wo_user.users = new_users
                    new_polls.append(poll_wo_user)

            elif (from_dateobj > p.datetime and to_dateobj < p.end_datetime):
                poll_with_user0 = Datepoll(datetime=p.datetime, end_datetime=from_dateobj)
                poll_wo_user = Datepoll(datetime=from_dateobj, end_datetime=to_dateobj)
                poll_with_user1 = Datepoll(datetime=to_dateobj, end_datetime=p.end_datetime)
                new_polls.extend([poll_with_user0, poll_with_user1])
                poll_with_user0.users = p.users
                poll_with_user1.users = p.users
                users = p.users
                users.remove(user)
                if len(users) > 0:
                    poll_wo_user.users = users
                    new_polls.append(poll_wo_user)
                old_polls.append(p)


            # TODO
        for poll in new_polls:
            self.append_datepoll(poll)
        save(updated_polls)
        delete(old_polls)

    def __interval_times(self, from_dateobj, to_dateobj, poll):
        time0 = min(from_dateobj, poll.datetime)
        time1 = max(from_dateobj, poll.datetime)
        time2 = min(poll.end_datetime, to_dateobj)
        time3 = max(poll.end_datetime, to_dateobj)
        return (time0, time1, time2, time3)

