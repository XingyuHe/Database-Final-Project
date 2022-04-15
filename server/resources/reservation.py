from flask_restful import Resource
from flask import abort

from db import db_engine, table_schema

class Reservation(Resource):

    __restaurant_table_name__ = "RESTAURANTS"
    __area_table_name__ = "AREAS"

    def get(self, restaurant_id):

        restaurant_found = self.find_restaurant(restaurant_id)

        print("restaurant {restaurant_id} found: {restaurant}".format(
            restaurant_id=restaurant_id, restaurant=restaurant_found))

        return restaurant_found
        
    @classmethod
    def find_restaurant(cls, restaurant_id):
        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")
        

        query = """
        SELECT * FROM {table_name_1} AS R, {table_name_2} AS A
        WHERE restaurant_id=%s and R.zipcode = A.zipcode
        """.format(
            table_name_1 = cls.__restaurant_table_name__,
            table_name_2 = cls.__area_table_name__
        )

        result = db_conn.execute(query, restaurant_id)
        restaurant = result.fetchone()
        print("restaurant: ", restaurant)
        if restaurant:
            restaurant = dict(zip(table_schema.restaurant_schema + table_schema.area_schema, restaurant))
        db_conn.close()
        return restaurant


