from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from ..utils import FB_GRAPH_URL, MESNGR_API_URL, fetch_user_data
from config import TOKEN
from . import auth
from .. import db
from ..models import User

@auth.route('/register/<messenger_uid>' , methods=['GET','POST'])
def register(messenger_uid):
    print(messenger_uid)
    if request.method == 'GET':
        return render_template('register.html')
    user = User(username=request.form['username'] ,
                password=request.form['password'],
                messenger_uid=messenger_uid)
    print(user)
    user_details_params = {'fields':'first_name,last_name,profile_pic',
                           'access_token':TOKEN}
    user_data = fetch_user_data(FB_GRAPH_URL + messenger_uid,
                                user_details_params)
    print(user_data)
    user.first_name = user_data["first_name"]
    user.last_name = user_data["last_name"]
    db.session.add(user)
    db.session.commit()
    print('User successfully registered')
    login_user(user, remember = True)
    return redirect(request.args.get('next') or url_for('main.index'))

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        print('hello')
        x =  render_template('login.html')
        return x
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username).first()
    print(registered_user)
    if (registered_user is None or
        not registered_user.verify_password(password)):
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('main.login'))
    login_user(registered_user, remember = True)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('main.index'))
