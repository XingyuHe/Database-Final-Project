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
    __area_table_name__ = "AREAS"

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

        query = "SELECT * FROM {table_name} WHERE name=%s".format(
            table_name=cls.__search_table_name__)

        result = db_conn.execute(query, search_args['search_keywords'])

        restaurant_rows = result.fetchall()

        search_results = []
        if restaurant_rows:
            for r in restaurant_rows:
                query = "SELECT zipcode, city, state from {table_name} WHERE area_id=%s".format(
                    table_name=cls.__area_table_name__)
                result = db_conn.execute(query, r[3])
                area_result = result.fetchone()
                print("area_result: ", area_result)
                search_results.append({
                    'restaurant_id': r[0],
                    'name': r[2],
                    'zipcode': area_result[0],
                    'city': area_result[1],
                    'state': area_result[2],
                    'intro': r[5]})
        db_conn.close()
        return search_results
