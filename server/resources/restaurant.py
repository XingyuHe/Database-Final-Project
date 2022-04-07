import string
from typing_extensions import Required
from flask_restful import Resource
from flask import (
    request, abort, session,
    redirect, render_template,
    make_response, flash, jsonify
)
from marshmallow import Schema, fields

from db import db_engine
from sqlalchemy import exc

class RestaurantQuerySchema(Schema):
    restaurant_id = fields.Int(required=True)

class Restaurant(Resource):
    __restaurant_table_name__ = "RESTAURANTS"
    __review_consumer_table_name = "ReviewsConsumersRestaurantsRelationship"
    __area_table_name__ = "AREAS"
    __image_consumer_restaurant_table_name__ = "ImagesConsumersRestaurantsRelationship"
    __image_table_name__ = "Images"

    def get(self):
        errors = RestaurantQuerySchema.validate(request.args)
        if errors:
            print(str(errors))
            abort(400, str(errors))

        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        restaurant_attr = self.getRestaurantAttributes(db_conn, request.form['restaurant_id'])
        reviews = self.getReviews(db_conn, request.form['restaurant_id'])

        return jsonify({
            "restaurant_attributes": restaurant_attr,
            "reviews": reviews
        })


    @classmethod
    def getReviews(cls, db_conn, restaurant_id):

        query_rows = db_conn.execute(
            """
            SELECT *
            FROM (?) AS R
            WHERE R.restaurant_id = %i
            """,
            cls.__review_consumer_table_name, restaurant_id
        ).fetchall()

        review_result = []
        for row in query_rows:

            review_result.append(
                {
                    "content": row[2],
                    "original_date": row[3],
                    "last_updated_date": row[4],
                    "overall_score": row[5],
                    "food_quality_score": row[6],
                    "service_score": row[7],
                    "ambience_score": row[8],
                    "value_score": row[9],
                    "image_urls": []
                }
            )

            review_img_query_rows = db_conn.execute(
                """
                SELECT I.image_id
                FROM (?) AS I
                WHERE I.consumer_id = %i AND I.restaurant_id = %i
                """,
                cls.__image_consumer_restaurant_table_name__,
                row[0], row[1]
            ).fetchall()

            for img_row in review_img_query_rows:
                img_result = db_conn.execute(
                    """
                    SELECT url
                    FROM (?) AS I
                    WHERE I.image_id = %i
                    """,
                    cls.__image_table_name__, img_row[0]
                ).fetchone()

                review_result[-1]["image_urls"].append(img_result[0])

        return review_result

    @classmethod
    def getRestaurantAttributes(cls, db_conn, restaurant_id):

        query_row = db_conn.execute(
            "SELECT * FROM (?) WHERE restaurant_id=%i",
            cls.__restaurant_table_name__, restaurant_id
        ).fetchone()

        area_query = "SELECT zipcode, city, state from {table_name} WHERE area_id=%s".format(
            table_name=cls.__area_table_name__)
        result = db_conn.execute(area_query, query_row[3])
        area_result = result.fetchone()
        print("area_result: ", area_result)

        query_result = {'restaurant_id': query_row[0],
                        'name': query_row[2],
                        'zipcode': area_result[0],
                        'city': area_result[1],
                        'state': area_result[2],
                        'intro': query_row[5]}

        return query_result