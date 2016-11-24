from flask import render_template, flash, redirect, url_for, session, request, g
from flask.ext.login import login_user, logout_user, current_user
from app import app, mongo, lm
#from .forms import LoginForm
from flask import jsonify
from datetime import datetime
from .models import User
from bson.objectid import ObjectId


# this sets the callback for reloading a user from the session
# the function you set should take a user ID (a unicode) and
# return a user object, or None if the user does not exist.
@lm.user_loader
def load_user(id):
    print(id)
    user = mongo.db.users.find_one({'_id': ObjectId(id)})
    print('USER: ' + str(user))
    if not user:
        return None
    return User(user['_id'], (user['first_name'] + ' ' + user['last_name']))



@app.route('/base')
def images():
    return render_template('base_alamo.html',
                           title = 'Test')

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    # current_user is a global variable representing the current user logged in
    # we are checking to see if anyone is logged in and based on that, we show a specific template
    if current_user.is_authenticated:
        return render_template('home-logged.html')
    else:
        return render_template('home.html')




@app.route('/home_logged')
def home_logged():
    print('### ' + str(current_user))
    print('### ' + str(current_user.is_authenticated))
    return render_template('home-logged.html')




@app.route('/login', methods=['POST'])
def login():
    print('TESTING: ' + (str(request.base_url)))
    page_requesting = request.referrer
    print('Page requesting:' + str(page_requesting))
    print('Email: ' + (str(request.form['email'])))
    print('Password: ' + (str(request.form['password'])))

    # pulling mongoDB users
    users = mongo.db.users
    user = users.find_one({'email': request.form['email']})
    if user == None:
        flash('That user does not exist')
        #return redirect(url_for('home'))
        return redirect(page_requesting)

    if ((user['email'] == request.form['email']) & (user['pass'] == request.form['password'])):

        # updating the last login time for the user in the database
        timestamp = datetime.today()
        users.update_one({'_id': user['_id']},
                         {'$set': {'last_login': timestamp}})

        # Pull the employee account information
        employee_info = {'id': user['_id'], 'first_name': user['first_name'], 'last_name': user['last_name'],
                         'last_login': user['last_login'],
                         'privilege_level': user['privilege_level']}

        for key in employee_info:
            print(str(key) + ' : ' + str(employee_info[key]))

        user_obj = User(user['_id'], (user['first_name'] + ' ' + user['last_name']))
        login_user(user_obj)

        # storing the name of the user into the global session variable
        # so that we can check if someone is logged in and display their name
        name = employee_info['first_name'] + ' ' + employee_info['last_name']
        session['name'] = name


        #return jsonify({'result': employee_info})
        #return redirect(url_for('home_logged'))
        return redirect(page_requesting)
        #return render_template('home-logged.html')
        #return redirect(url_for('home'))

    else:
        flash('Invalid Username or Password')
        return redirect(page_requesting)

    return redirect(url_for('home'))



@app.route("/logout")
def logout():
    logout_user()
    page_requesting = request.referrer
    return redirect(page_requesting)



@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/walls")
def walls():
    return render_template('walls.html')


@app.route("/map")
def map():
    return render_template('map.html')

@app.route("/wall_a")
def wall_a():
    return render_template('search_wall_TESTING.html')
