# -*- encoding: utf-8 -*-
import sys, os

sys.path.insert(0, os.getcwd()+'/src/main/python')

from flask import Flask, render_template, redirect, request
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
        if not utils.check_credentials(request.form['username'], hashlib.md5(request.form['password'].encode()).hexdigest()):
            error = 'Invalid Credentials. Please try again.'
        else:
            token = utils.generate_token(user_id, utils.get_auth_token(
                request.form['username'], hashlib.md5(request.form['password'].encode()).hexdigest()))
            invite = variables.link + token
            return redirect(invite)
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
