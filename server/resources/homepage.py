from flask_restful import Resource
from flask import make_response, render_template, session

class Homepage(Resource):

    def get(self):
        if 'username' in session:
            return make_response(render_template("home_res.html"), 200, {'Content-Type': 'text/html'})
        else:
            return make_response(render_template("home.html"), 200, {'Content-Type': 'text/html'})