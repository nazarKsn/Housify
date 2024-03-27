#!/usr/bin/env python3
"""Flask app"""
from flask import Flask, request, render_template, session, abort
from flask import redirect, send_from_directory
from waitress import serve
import time
import json
import sys
import os
from src.utils import DOS, format_res_obj, sort_by_date_key
from src.mongo import DBClient
from bson.objectid import ObjectId

app = Flask(__name__, static_folder=f"templates")
app.secret_key = (b'3ec87ffa74e857c9ab4aa4048cc8400be4522704a65c33adb50d34bb'
                  b'e55edde8')
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SAMESITE='Lax',
)


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DB = DBClient('LordsProperties')
users_table = 'users'
properties_table = 'properties'


@app.before_request
def before_request():
    ua = request.headers.get('user-agent')
    is_bot = DOS().is_bot(ua)
    if is_bot:
        if request.headers.getlist('X-Forwarded-For'):
            ip = request.headers.getlist('X-Forwarded-For')[0]
        else:
            ip = request.remote_addr
        print(f'New connection from Bot {ip}')
        abort(501)

    excluded_paths = ['/sign-in', '/sign-out', '/sign-up']
    if not session.get('url'):
        session['url'] = '/'

    if (request.path not in excluded_paths and
            not request.path.startswith('/templates')):
        session['url'] = request.environ['RAW_URI']


@app.route('/sendImg', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'upload-photo' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['upload-photo']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

            return redirect(url_for('uploaded_photo', filename=filename))
    return render_template('upload_picture.html', error=None)


@app.route('/uploads/<filename>')
def uploaded_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def index():
    available_houses = DB.find(properties_table, {'status': 'rent'})

    available_houses = sorted(available_houses, key=sort_by_date_key,
                              reverse=True)

    available_houses = list(map(format_res_obj, available_houses))

    return render_template(f'public/index.html', data=session,
                           for_rent=available_houses)


@app.route('/search')
def search():
    location = request.args.get('location')
    status = request.args.get('status')
    min_bathrooms = request.args.get('bathrooms')
    min_bedrooms = request.args.get('bedrooms')

    _filter = {}
    filters = {}

    if location:
        _filter = {'$or': [{'country': location}, {'state': location},
                           {'city': location}, {'address': location}]}
        filters['location'] = location

    if status and status != 'any':
        _filter['status'] = status
    filters['status'] = status

    if min_bathrooms:
        _filter['bathrooms'] = {'$gt': int(min_bathrooms)}
        filters['bathrooms'] = min_bathrooms

    if min_bedrooms:
        _filter['bedrooms'] = {'$gt': int(min_bedrooms)}
        filters['bedrooms'] = min_bedrooms

    available_houses = DB.find(properties_table, _filter)
    available_houses = list(map(format_res_obj, available_houses))

    return render_template('public/search.html', data=session,
                           houses=available_houses, filters=filters)


@app.route('/preview/<apartment_id>')
def preveiw(apartment_id):
    house = DB.find_one(properties_table, {'_id': ObjectId(apartment_id)})
    house = format_res_obj(house)

    return render_template(f'public/preview.html', data=session,
                           apartment=house)


# Sign-up and sign-in post and get
@app.route('/sign-up')
def sign_up_get():
    return render_template(f'public/sign-up.html', data="")


@app.route('/sign-in')
def sign_in_get():
    return render_template(f'public/sign-in.html', data="")


@app.route('/sign-up', methods=['POST'])
def sign_up_post():
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    dob = request.form['dob']

    if DB.find_one(users_table, {'email': email}):
        flash('That email already exists')
        return redirect(request.url)

    new_user_info = {
        'email': email,
        'password': bcrypt.hashpw(password.encode(), bcrypt.gensalt()),
        'dob': dob, 'status': 'online',
        "username": username}

    DB.insert_one(users_table, new_user_info)
    return render_template(f'public/sign-in.html', data=session)


@app.route('/sign-in', methods=['POST'])
def sign_in_post():
    email = request.form['email']
    pwd = request.form['password']

    try:
        user = DB.find_one(users_table, {'email': email})
        if user and bcrypt.checkpw(pwd.encode(), user['password']):
            user = {'username': user['username'],
                    'email': user['email'],
                    'id': str(user['_id'])}
            session['user'] = user

            DB.update_one(users_table,
                          {'username': session['user']['username']},
                          {'$set': {'status': 'online'}})
            return redirect(session['url'])
        else:
            flash("You have entered an invalid email or password")
            return redirect(request.url)
    except Exception as e:
        print(e)
        flash('Error signing in. Please try again.')
        return redirect(request.url)


@app.route('/sign-out')
def sign_out():
    try:
        DB.update_one(users_table,
                      {'username': session['user']['username']},
                      {'$set': {'status': 'offline'}})
    except Exception:
        pass

    last_page = session['url']
    session.clear()

    return redirect(last_page)


if __name__ == "__main__":
    print('Server is running...')
    app.run(debug=True, port=5000, host='0.0.0.0')
    # serve(app, host='0.0.0.0', port=80, threads=100)
