from email import header
from http.client import REQUEST_ENTITY_TOO_LARGE
import json
from flask_restful import Resource
from flask import (
    request, abort, jsonify, session, redirect, url_for, render_template, make_response
)
from marshmallow import Schema, fields

from db import db_engine


class LoginQuerySchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


loginQuerySchema = LoginQuerySchema()


class Login(Resource):

    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("login.html"), 200, headers)
        # TODO return message to front end to require a post method
        # this is currently or testing purpose

    def post(self):
        print("login-args:", request.args)
        errors = loginQuerySchema.validate(request.form)
        if errors:
            print(str(errors))
            abort(400, str(errors))

        login_ok = self.login_auth(request.args)

        if login_ok:
            session['username'] = request.form['username']
            return make_response(redirect('/'))
        return make_response('login failed')


    @classmethod
    def login_auth(cls, login_args):
        print("login-args:", login_args)
        # authenticate
        # TODO: implement authentication
        return True


# Set the secret key to some random bytes. Keep this really secret!
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         return redirect(url_for('index'))
#     return '''
#         <form method="post">
#             <p><input type=text name=username>
#             <p><input type=submit value=Login>
#         </form>
#     '''

# @app.route('/logout')
# def logout():
#     # remove the username from the session if it's there
#     session.pop('username', None)
#     return redirect(url_for('index')