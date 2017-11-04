from app import app, lm
from flask import request, redirect, render_template, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from json import dumps as jsonDumps
from time import time

from .forms import LoginForm, RegisterForm, YarnersForm, ProfileForm, NewYarnerForm
from .helper import Helper
from .yarner import Yarner
from .yarn import YarnForm, Yarn

#### Ajax return helpers
def ajaxOK(msg):
    return ajaxMsg(msg, 200)

def ajaxFail(msg):
    return ajaxMsg(msg, 500)

def ajaxMsg(msg, status):
    return jsonDumps({'message':msg}), status, {'ContentType':'application/json'}

#### Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        yarnersForm = YarnersForm()
        yarners = sorted(list(current_user.get_yarners()), key=lambda y: y['name'])
        print(yarners)
        yarnersForm.yarners.choices = [(y['_id'], y['name']) for y in yarners]

        profileForm = ProfileForm(email=current_user.email, name=current_user.name)
        newYarnersForm = NewYarnerForm()
        helper = current_user
        return render_template('menu.html', title='Yarnings', yarnersform=yarnersForm, profileform=profileForm, newyarnerform=newYarnersForm, helper=helper)
    loginForm = LoginForm()
    registerForm = RegisterForm()
    return render_template('home.html', title='Yarnings', loginform=loginForm, registerform=registerForm)

@app.route('/new-yarner', methods=['POST'])
@login_required
def new_yarner():
    form = NewYarnerForm()
    if form.validate_on_submit():
        name = form.name.data
        hibiscus = form.hibiscus.data
        tYarner = Yarner(name, hibiscus, current_user.get_id())

        if (tYarner.insertDB()):
            flash("Yarner created successfully", category='success')
            current_user.set_yarner(tYarner.get_hibiscus())

            if (form.ajax.data == "True"):
                return ajaxOK("Yarner Created Successfully!");
            return redirect(url_for("new_yarn"))
        return ajaxFail("HBCIS already registered")
    #flash("Bad input. Please check fields.", category='error')
    return ajaxFail("Failed to validate fields. Please check input.")

@app.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data
        email = form.email.data
        name = form.name.data
        tHelper = Helper(user, email, name)

        if (tHelper.insertDB(password)):
            flash("Account created successfully", category='success')
            user = app.config['HELPERS_COLLECTION'].find_one({"_id": form.username.data})
            user_obj = Helper(user['_id'], user['email'], user['name'])
            login_user(user_obj)
            if (form.ajax.data == "True"):
                return ajaxOK("Registration Successful!");
            return redirect(request.args.get("next") or url_for("home"))
        return ajaxFail("Username already registered")
    #flash("Bad input. Please check fields.", category='error')
    return ajaxFail("Failed to validate fields. Please check input.")

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = app.config['HELPERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and Helper.validate_login(user['password'], app.config['SALT'] + form.password.data):
            user_obj = Helper(user['_id'], user['email'], user['name'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            if (form.ajax.data == "True"):
                return ajaxOK("Login Successful!");
            else:
                return redirect(request.args.get("next") or url_for("home"))
        if (form.ajax.data == "True"):
            return ajaxFail("Wrong username or password")
        else:
            flash("Wrong username or password", category='error')
            loginForm = LoginForm()
            registerForm = RegisterForm()
            return redirect(url_for("home"))
    flash("Bad input. Please check fields.", category='error')
    return ajaxFail
  
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile-update', methods=['POST'])
@login_required
def profile_update():
    form = ProfileForm()
    if form.validate_on_submit():
        password = form.password.data
        email = form.email.data
        name = form.name.data

        if (current_user.update(email, name, password)):
            flash("Profile successfully", category='success')
            user = app.config['HELPERS_COLLECTION'].find_one({"_id": current_user.get_id()})
            user_obj = Helper(user['_id'], user['email'], user['name'])
            login_user(user_obj)
            if (form.ajax.data == "True"):
                return ajaxOK("Profile updated successful!");
            return redirect(request.args.get("next") or url_for("home"))
        return ajaxFail("Failed to update profile")
    #flash("Bad input. Please check fields.", category='error')
    return ajaxFail("Failed to validate fields. Please check input.")

#### TO IMPLEMENT
@app.route('/new-yarn', methods=['GET'])
@login_required
def new_yarn():
    if current_user.get_yarner() == None:
        return redirect(url_for("home"))
    if current_user.get_yarn() == None:
        current_user.set_yarn == int(time())
    tYarner = app.config['YARNERS_COLLECTION'].find_one({"_id": current_user.get_yarner()})
    tYarn = Yarn(tYarner['name'], current_user.get_yarner(), current_user.get_yarn(), current_user.get_id())
    if tYarn.insertDB():        
        return redirect(url_for("yarn"))
    flash("Unable to start a new yarn", category='error')
    return render_template('menu.html')

@app.route('/continue-yarn',  methods=['GET'])
@login_required
def continue_yarn():
    form = YarnerForm()
    if form.validate_on_submit():
        yarnerId = form.yarner.data
        tYarner = app.config['YARNERS_COLLECTION'].find_one({"_id": yarnerId})

@app.route('/yarn', methods=['GET'])
@login_required
def yarn():
    if current_user.get_yarner() == None:
        return redirect(url_for("home"))
    form = YarnForm()
    if current_user.get_yarn() == None:
        current_user.set_yarn == int(time())
    tYarn = Yarn.get(current_user.get_yarner(), current_user.get_yarn())
    return render_template('example.html')

@app.route('/yarn-update', methods=['POST'])
@login_required
def yarn_update():
    form = YarnForm()
    if form.validate_on_submit():
        yarn

#### Static (move to nginx in prod)
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('lib', path)

@app.route('/plugin/<path:path>')
def send_plugin(path):
    return send_from_directory('plugin', path)

#### Login Manager helpers
@lm.user_loader
def load_user(username):
    u = app.config['HELPERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return Helper(u['_id'], u['email'], u['name'])
