from email import header
from http.client import REQUEST_ENTITY_TOO_LARGE
import string
from flask_restful import Resource
from flask import (
    request, abort, jsonify, session,
    redirect, url_for, render_template,
    make_response, flash
)
from marshmallow import Schema, fields
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from db import db_engine
from sqlalchemy import exc


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
        print("login-args:", request.form)
        errors = loginQuerySchema.validate(request.form)
        if errors:
            print(str(errors))
            abort(400, str(errors))

        error = self.login(request.form)

        if error == None:
            session['username'] = request.form['username']
            return make_response(redirect('/'))

        flash(error)
        headers = {'Content-Type': 'text/html'}
        print(error)
        return make_response(render_template("login.html"), 200, headers)


    @classmethod
    def login(cls, login_args):
        print("login-args:", login_args)
        # authenticate
        username = login_args["username"]
        password = login_args["password"]
        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        error = None
        user = db_conn.execute(
            "SELECT * FROM Consumers AS C WHERE C.username = %s", username
            ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["hashed_password"], password):
            error = "Incorrect password."

        return error

class SignupQuerySchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    email = fields.Str(required=True)
    telephone = fields.Str(required=True)
    zipcode = fields.Str(required=True)

signupQuerySchema = SignupQuerySchema()

def updateDB_addNewConsumer(db_conn, username, password, email, telephone, zipcode) -> string:
    error = None

    # to prevent zipcode foreign key integrity violation
    if not checkDB_area(db_conn, zipcode):
        updateDB_addNewArea(db_conn, zipcode)

    try:
        db_conn.execute(
            "INSERT INTO Consumers (username, hashed_password, email, telephone, zipcode) VALUES\
                (%s, %s, %s, %s, %s) ",
            username, generate_password_hash(password), email, telephone, zipcode
        )
    except exc.IntegrityError:
        # The username was already taken, which caused the
        # commit to fail. Show a validation error.
        error = f"User {username} is already registered."

    return error

def checkDB_area(db_conn, zipcode):
    res = db_conn.execute(
        "SELECT A.zipcode FROM Areas AS A WHERE A.zipcode = %s", zipcode
        ).fetchone()

    return res != None


def updateDB_addNewArea(db_conn, zipcode) -> bool:
    # TODO: perhaps add city and state information afterwards
    db_conn.execute(
        "INSERT INTO Areas (zipcode) VALUES (%s)", zipcode
    )


class Signup(Resource):
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template("signup.html"), 200, headers)

    def post(self):

        args_error = signupQuerySchema.validate(request.form)
        if args_error:
            print(str(args_error))
            abort(400, str(args_error))

        signup_error = self.signup(request.form)

        headers = {'Content-Type': 'text/html'}
        if signup_error == None:
            # signup succeeds
            return make_response(render_template("login.html"), 200, headers)
        else:
            # signup fails
            flash(signup_error)
            return make_response(render_template("signup.html"), 200, headers)


    @classmethod
    def signup(cls, signup_args):

        username = signup_args["username"]
        password = signup_args["password"]
        email = signup_args["email"]
        telephone = signup_args["telephone"]
        zipcode = signup_args["zipcode"]
        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif not email:
            error = "Password is required."
        elif not telephone:
            error = "Telephone is required."
        elif not zipcode:
            error = "Zipcode is required."

        if error is None:
            error = updateDB_addNewConsumer(db_conn, username, password, email, telephone, zipcode)

        return error
