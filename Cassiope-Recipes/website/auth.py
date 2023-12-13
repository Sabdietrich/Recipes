from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

stores = [
    {
        "name": "store",
        "items": [
            {
                "name": "chair",
                "price": 15
            }
        ]
    }
]

@auth.get("/store")
def get_stores():
    return {"stores": stores}

@auth.post("/store")
def create_store():
    request_data = request.get_json()
    new_store = {"name": request_data["name"], "items":[]}
    stores.append(new_store)
    return new_store, 201

@auth.post("/store/<string:name>/item")
def create_item(name):
    request_data = request.get_json()
    for store in stores:
        if store["name"] == name:
            new_item = {"name": request_data["name"], "price": request_data["price"]}
            store["items"].append(new_item)
            return new_item, 201
    return {"message": "Store not found"}, 404


@auth.get("/store/<string:name>")
def get_store(name):
    for store in stores:
        if store["name"] == name:
            return store
    return {"message": "Store not found"}, 404


@auth.get("/store/<string:name>/item")
def get_item_in_store(name):
    for store in stores:
        if store["name"] == name:
            return {"items": store["items"]}
    return {"message": "Store not found"}, 404


login = [
    {
        "email": "claudia@gmail",
        "password": "claudia123"
    }
]

@auth.get("/login")
def get_login():
    return {"login": login}

@auth.post("/login")
def create_login():
    request_data = request.get_json()
    new_login = {"email": request_data["email"], 
                 "password": request_data["password"]}
    login.append(new_login)
    user = User.query.filter_by(email=request_data["email"]).first()
    if user:
        if check_password_hash(user.password, request_data["password"]):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Incorrect password, try again.', category='error')
    else:
        flash('Email does not exist.', category='error')
    return new_login, 201


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

signup = [
    {
        "email": "claudia@gmail",
        "firstName": "Claudia",
        "password1": "claudia123",
        "password2": "claudia123"
    }
]

@auth.get("/signup")
def get_signup():
    return {"login": signup}

@auth.get("/user")
def get_user():
    return {"user": User}

@auth.post("/signup")
def create_signup():
    request_data = request.get_json()
    new_signup = {"email": request_data["email"], 
                  "firstName": request_data["firstName"], 
                  "password1": request_data["password1"], 
                  "password2": request_data["password2"]}
    #so posso dar append se cumprir tds os ifs
    signup.append(new_signup)

    user = User.query.filter_by(email=request_data["email"]).first()
    if user:
        flash('Email already exists.', category='error')
    elif len(request_data["email"]) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(request_data["firstName"]) < 2:
        flash('First name must be greater than 1 character.', category='error')
    elif request_data["password1"] != request_data["password2"]:
        flash('Passwords don\'t match.', category='error')
    elif len(request_data["password1"]) < 7:
        flash('Password must be at least 7 characters.', category='error')
    else:
        new_user = User(email=request_data["email"], first_name=request_data["firstName"], password=generate_password_hash(
            request_data["password1"], method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        flash('Account created!', category='success')
        return redirect(url_for('views.home'))
    
    return new_signup, 201


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        data = request.form
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
