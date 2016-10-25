from flask import render_template, flash, redirect
from app import app, mongo
from .forms import LoginForm
from flask import jsonify
from datetime import datetime


@app.route('/')
@app.route('/index')
def alamo():
    return render_template('alamo.html',
                           title='Home')

@app.route('/base')
def images():
    return render_template('base_alamo.html',
                           title = 'Test')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        users = mongo.db.users
        user = users.find_one({'email': form.email.data})
        print(user)
        if user == None:
            flash('That user does not exist')
            return render_template('login.html', title='Sign In', form = form)

        if ((user['email'] == form.email.data) & (user['pass'] == form.password.data)):
            flash('Success')

            # updating the last login time for the user in the database
            date = datetime.today()
            users.update_one({'user_id':user['user_id']},
                             {'$set':{'last_login': date}})

            #Pull the employee account information
            employee_info = {'id': user['user_id'], 'first name' : user['first_name'], 'last name' : user['last_name'], 'last_login': user['last_login'],
                     'privilege_level': user['privilege_level']}

            return jsonify({'result' : employee_info})
        else:
            flash('Invalid Username or Password')
            return render_template('login.html', title='Sign In', form=form)


    return render_template('login.html',
                           title='Sign In',
                           form = form)



@app.route('/example')
def index():
    user = {'nickname': 'Miguel'}
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)

