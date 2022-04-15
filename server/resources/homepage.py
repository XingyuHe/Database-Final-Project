from flask_restful import Resource
from flask import make_response, render_template

class Homepage(Resource):

    def get(self):
        return make_response(render_template("home.html"), 200, {'Content-Type': 'text/html'})