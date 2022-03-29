from flask_restful import Resource

class Homepage(Resource):

    def get(self):
        return "<p>Database Final Project by Peter He and Zhe Hua</p>"