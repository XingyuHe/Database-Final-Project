import json
from flask_restful import Resource
from flask import request, abort, jsonify
from marshmallow import Schema, fields

from db import db_engine

class SearchQuerySchema(Schema):
    search_keywords = fields.Str(required=True)
    search_location = fields.Str(required=True)

searchQuerySchema = SearchQuerySchema()

class Search(Resource):

    __search_table_name__ = "RESTAURANTS"
    
    def get(self):
        errors = searchQuerySchema.validate(request.args)
        if errors:
            print(str(errors))
            abort(400, str(errors))
        
        restaurants_found = self.find_restaurants(request.args)
        if restaurants_found:
            return jsonify(restaurants_found)

        return {'message': "No results for {}".format(request.args['search_keywords'])}
        
    @classmethod
    def find_restaurants(cls, search_args):
        print("search_args: ", search_args)
        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        query = "SELECT * FROM {table_name} WHERE name=%s".format(table_name=cls.__search_table_name__)

        result = db_conn.execute(query, search_args['search_keywords'])

        rows = result.fetchall()
        db_conn.close()

        if rows:
            print("rows: ", rows)
            return rows

    
        