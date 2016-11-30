from flask import render_template, flash, redirect, url_for, session, request
from flask.ext.login import login_user, logout_user, current_user
from app import app, mongo, lm
from datetime import datetime
from .models import User
from bson.objectid import ObjectId
import json



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


@app.route('/login', methods=['POST'])
def login():
    #print('TESTING: ' + (str(request.base_url)))
    page_requesting = request.referrer
    #print('Page requesting:' + str(page_requesting))
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


# created custom JSON encoder to handle and serialize the mongoDB ObjectIDs
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


# created custom route in flask app so that it could handle all walls.
@app.route("/walls/<wall_letter>")
def wall(wall_letter):
    # create list to store all of the  Openlayers 3 layers in the database that pertain to the specific wall
    layers = []
    # retrieve the collection for the specified wall
    collection = mongo.db[wall_letter]
    # if the collection contains no documents (drawing layers made from OpenLayers 3) then return an empty list
    if(collection.count() == 0):
        return layers
    # find all documents in the wall collection and put them into a list to give to the front end
    documents = collection.find({})
    for document in documents:
        json_document = JSONEncoder().encode(document)
        layers.append(json_document)


    # this was implemented so that once other walls are added, it could
    # dynamically render the correct wall html based on the wall specified
    return render_template(wall_letter + '.html', layers=layers)
    #return render_template('wall_a_new.html')

# adding a detail to the wall
@app.route("/wall_form", methods=['POST'])
def wall_form():
    # save the page requesting to return back to it
    page_requesting = request.referrer
    print(page_requesting)
    # pull the end of the request referrer url to get the corresponding wall letter
    wall_letter = page_requesting.split('/')[-1]

    # pull the json content
    content = request.json

    # test printing
    print(content)
    print(json.dumps(content, sort_keys = True, indent = 4, separators = (',', ': ')))

    # pulling mongoDB wall collection
    wall = mongo.db[wall_letter]
    wall.insert_one(content)

    # return to the page that performed the request
    return redirect(page_requesting)
