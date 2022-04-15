from flask_restful import Resource
from flask import request, abort, jsonify
from marshmallow import Schema, fields

from db import db_engine, table_schema


class SearchQuerySchema(Schema):
    search_keyword = fields.Str(required=True)
    search_city = fields.Str(required=True)
    search_cuisine = fields.Str(required=True)
    search_hashtag = fields.Str(required=True)


searchQuerySchema = SearchQuerySchema()


class Search(Resource):

    __restaurants_table_name__ = "RESTAURANTS"
    __areas_table_name__ = "AREAS"
    __cuisines_table_name__ = "CUISINES"
    __cuisinesrestaurantsrelationship_table_name__ = "CuisinesRestaurantsRelationship"
    __hashtagsconsumersrestaurantsrelationship_table_name__ = "HashtagsConsumersRestaurantsRelationship"
    __hashtags_table_name__ = "HASHTAGS"

    def get(self):
        errors = searchQuerySchema.validate(request.args)
        if errors:
            print(str(errors))
            abort(400, str(errors))

        restaurants_found = self.find_restaurants(request.args)
        if restaurants_found:
            return jsonify(restaurants_found)

        return {'message': "No results found"}

    @classmethod
    def find_restaurants(cls, search_args):
        print("search_args: ", search_args)
        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        query = """
        SELECT * FROM {table_name_1} AS R, {table_name_2} AS A,
            {table_name_3} AS CR, {table_name_4} AS C,
            {table_name_5} AS HR, {table_name_6} AS H
        WHERE LOWER(R.restaurant_name) LIKE LOWER(%(x)s)
            AND LOWER(A.city) = (CASE WHEN %(y)s = '' THEN LOWER(A.city) ELSE LOWER(%(y)s) END)
            AND R.zipcode = A.zipcode AND R.restaurant_id = CR.restaurant_id AND C.cuisine_id = CR.cuisine_id
            AND LOWER(C.cuisine_name) = (CASE WHEN %(z)s = '' THEN LOWER(C.cuisine_name) ELSE LOWER(%(z)s) END)
            AND R.restaurant_id = HR.restaurant_id AND H.hashtag_id = HR.hashtag_id
            AND LOWER(H.hashtag_name) = (CASE WHEN %(w)s = '' THEN LOWER(H.hashtag_name) ELSE LOWER(%(w)s) END)
        """.format(
            table_name_1=cls.__restaurants_table_name__,
            table_name_2=cls.__areas_table_name__,
            table_name_3=cls.__cuisinesrestaurantsrelationship_table_name__,
            table_name_4=cls.__cuisines_table_name__,
            table_name_5=cls.__hashtagsconsumersrestaurantsrelationship_table_name__,
            table_name_6=cls.__hashtags_table_name__
        )

        result = db_conn.execute(query, x='%'+search_args['search_keyword']+'%', y=search_args['search_city'],
                                 z=search_args['search_cuisine'], w=search_args['search_hashtag'])
        restaurant_rows = result.fetchall()
        schema = table_schema.restaurant_schema + table_schema.area_schema + \
            table_schema.cuisine_restaurant_relationship_schema + \
            table_schema.cuisine_schema + \
            table_schema.hashtag_consumer_restaurant_relationship_schema + \
            table_schema.hashtag_schema
        search_results = {}

        if restaurant_rows:
            for row in restaurant_rows:
                restaurant = dict(zip(schema, row))

                if restaurant['restaurant_id'] in search_results:

                    if restaurant['cuisine_name'] not in search_results[restaurant['restaurant_id']]['cuisine_name']:
                        search_results[restaurant['restaurant_id']]['cuisine_name'].append(
                            restaurant['cuisine_name'])
                    elif restaurant['hashtag_name'] not in search_results[restaurant['restaurant_id']]['hashtag_name']:
                        search_results[restaurant['restaurant_id']]['hashtag_name'].append(
                            restaurant['hashtag_name'])

                else:
                    restaurant['cuisine_name'] = [restaurant['cuisine_name']]
                    restaurant['hashtag_name'] = [restaurant['hashtag_name']]
                    search_results[restaurant['restaurant_id']] = restaurant

        db_conn.close()
        return list(search_results.values())
