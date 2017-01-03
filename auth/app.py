# -*- encoding: utf-8 -*-
import sys, os

sys.path.insert(0, os.getcwd())

from flask import Flask, render_template, redirect, request
import requests
import json
import hashlib

from src.utils import Utils
import variables

utils = Utils()

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bienvenido!'

@app.route('/logged/<token>')
def logged(token=None):
    invite = variables.link + token
    return 'Logged! Use this link: %s' % invite

@app.route('/login/<user_id>', methods=['GET', 'POST'])
def login(user_id=None):
    error = None
    if request.method == 'POST':
        if not check_credentials(request.form['username'], hashlib.md5(request.form['password'].encode()).hexdigest()):
            error = 'Invalid Credentials. Please try again.'
        else:
            token = utils.generate_token(user_id)
            invite = variables.link + token
            return redirect(invite)
    return render_template('login.html', error=error)

def get_token(username, password):
    pre_token = username + hashlib.md5(password.encode()).hexdigest()
    token = username + ':' + hashlib.md5(pre_token.encode()).hexdigest()
    return token

def check_token(token):
    url = 'https://authb.agoraus1.egc.duckdns.org/api/index.php?method=checkToken&token=%s' % token
    response = requests.get(url)
    valid = json.loads(response.text.replace('\ufeff', ''))['valid']
    return valid

def check_credentials(username, password):
    token = get_token(username, password)
    return check_token(token)

if __name__ == '__main__':
    app.run(host='0.0.0.0')