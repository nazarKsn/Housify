#!/usr/bin/env python3
"""Flask app"""
from flask import Flask, request, render_template, session, abort
from flask import redirect, send_from_directory
from waitress import serve
import time
import json
import sys
import os
from src.utils import DOS
from src.mongo import DBClient

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


@app.route('/sendImg', methods=['POST'])
def upload_image():
    if request.headers.getlist('X-Forwarded-For'):
        ip = request.headers.getlist('X-Forwarded-For')[0]
    else:
        ip = request.remote_addr

    ua = request.headers.get('user-agent')
    device = DOS().is_bot(ua)
    if not device:
        if 'upload-photo' not in request.files:
            return 'No file part'

        file = request.files['upload-photo']
        if file.filename == '':
            return "No file"

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        cid = request.form.get('cid')
        c_info = DB.find_one(challenges_table, {"cid": cid})

        if str(session['user']['username']) == str(c_info['creator']):
            DB.update_one(challenges_table, {'cid': cid},
                          {"creators-prove": file.filename})
        else:
            DB.update_one(challenges_table, {'cid': cid},
                          {'$set': {"challengers-prove": file.filename}})

            return ('Successfully uploaded. '
                    'Please wait for moderators decision.')
        return render_template('upload_picture.html', error=None)
    else:
        print(f'New connection from Bot {ip}')
        return ('501')


@app.route('/uploads/<filename>')
def uploaded_photo(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def index():
    if request.headers.getlist('X-Forwarded-For'):
        ip = request.headers.getlist('X-Forwarded-For')[0]
    else:
        ip = request.remote_addr

    ua = request.headers.get('user-agent')
    device = DOS().is_bot(ua)
    if not device:
        print(f'New connection from {ip}')

        available_houses = DB.find(properties_table, {'status': 'rent'})
        print(available_houses)
        return render_template(f'public/index.html', data=session,
                               for_rent=available_houses)

    else:
        print(f'New connection from Bot {ip}')
        return ('501')


@app.route('/search')
def search():
    location = request.args.get('location')
    status = request.args.get('status')
    bathrooms = request.args.get('bathrooms')
    bedrooms = request.args.get('bedrooms')

    _filter = {}

    if location:
        _filter = {'$or': [{'country': location}, {'state': location},
                           {'city': location}, {'address': location}]}

    if status:
        _filter['status'] = status

    if bathrooms:
        _filter['bathrooms'] = bathrooms

    if bedrooms:
        _filter['bedrooms'] = bedrooms

    available_houses = DB.find(properties_table, _filter)
    return render_template('public/search.html', data=session,
                           houses=available_houses)


@app.route('/preview/<apartmentid>')
def preveiw(apartmentid):
    if request.headers.getlist('X-Forwarded-For'):
        ip = request.headers.getlist('X-Forwarded-For')[0]
    else:
        ip = request.remote_addr

    ua = request.headers.get('user-agent')
    device = DOS().is_bot(ua)
    if not device:
        available_houses = DB.find_one(properties_table,
                                       {'apartmentid': apartmentid,
                                        'status': 'rent'})

        return render_template(f'public/preview.html', data=session,
                               apartment=available_houses)
    else:
        print(f'New connection from Bot {ip}')
        return ('501')


# Sign-up and sign-in post and get
@app.route('/sign-up')
def sign_up_get():
    ua = request.headers.get('user-agent')
    is_bot = DOS().is_bot(ua)
    if not is_bot:
        return render_template(f'public/sign-up.html', data="")
    else:
        return ('501')


@app.route('/sign-in')
def sign_in_get():
    ua = request.headers.get('user-agent')
    is_bot = DOS().is_bot(ua)
    if not is_bot:
        return render_template(f'public/sign-in.html', data="")
    else:
        return ('501')


@app.route('/sign-up', methods=['POST'])
def sign_up_post():
    ua = request.headers.get('user-agent')
    is_bot = DOS().is_bot(ua)
    if not is_bot:
        email = request.form['email']
        password1 = request.form['password']
        password2 = request.form['confirm_password']
        username = request.form['username']
        dob = request.form['dob']

        new_user_info = {
            'email': email, 'password': password1,
            'dob': dob, 'status': 'online',
            "username": username}

        DB.insert_one(users_table, new_user_info)
        return render_template(f'public/sign-in.html', data=session)
    else:
        return ('501')


@app.route('/sign-in', methods=['POST'])
def sign_in_post():
    ua = request.headers.get('user-agent')
    is_bot = DOS().is_bot(ua)
    if not is_bot:
        email = request.form['email']
        pwd = request.form['password']
        info = {"email": email, "password": pwd}
        try:
            check_user = DB.find_one(users_table, info)
            check_user['_id'] = str(check_user['_id'])
            session.update({"user": check_user})

            try:
                if check_user['account_type'] == 'moderator':
                    session.update({"moderator": True})
                return redirect('moderator-index')
            except Exception:
                pass

            DB.update_one(users_table,
                          {'username': session['user']['username']},
                          {'$set': {'status': 'online'}})
            return render_template(f'public/index.html', data=session)
        except Exception as e:
            print(e)
            err_msg = ("we couldn't find acombination of that email and "
                       "password, try again.")

            return render_template(f'public/sign-in.html', data=session,
                                   error={'error': err_msg})
    else:
        return ('501')


@app.route('/sign-out')
def sign_out():
    ua = request.headers.get('user-agent')
    is_bot = DOS().is_bot(ua)
    if not is_bot:
        try:
            DB.update_one(users_table,
                          {'username': session['user']['username']},
                          {'$set': {'status': 'offline'}})
        except Exception:
            pass

        session.clear()
        return render_template(f'public/index.html', data="")
    else:
        return ('501')


if __name__ == "__main__":
    print('Server is running...')
    app.run(debug=True, port=5000, host='0.0.0.0')
    # serve(app, host='0.0.0.0', port=80, threads=100)
