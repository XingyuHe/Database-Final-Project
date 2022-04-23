from flask_restful import Resource
from flask import (
    abort, make_response, render_template
)

from db import db_engine, table_schema


class Restaurant(Resource):
    __restaurant_table_name__ = "RESTAURANTS"
    __review_consumer_table_name = "ReviewsConsumersRestaurantsRelationship"
    __area_table_name__ = "AREAS"
    __image_consumer_restaurant_table_name__ = "ImagesConsumersRestaurantsRelationship"
    __image_table_name__ = "Images"
    __cuisines_table_name__ = "CUISINES"
    __cuisinesrestaurantsrelationship_table_name__ = "CuisinesRestaurantsRelationship"
    __hashtagsconsumersrestaurantsrelationship_table_name__ = "HashtagsConsumersRestaurantsRelationship"
    __hashtags_table_name__ = "HASHTAGS"

    def get(self, restaurant_id):

        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        restaurant_attr = self.getRestaurantAttributes(db_conn, restaurant_id)
        reviews = self.getReviews(db_conn, restaurant_id)

        attr_review_data = {
            "att": restaurant_attr,
            "rev": reviews
        }

        return make_response(
            render_template(
                "restaurant.html", data=attr_review_data), 200, {'Content-Type': 'text/html'})


    @classmethod
    def getReviews(cls, db_conn, restaurant_id):

        query_rows = db_conn.execute(
            """
            SELECT *
            FROM {table_name} AS R
            WHERE R.restaurant_id = %s
            """.format(table_name=cls.__review_consumer_table_name),
            restaurant_id
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
                FROM {table_name} AS I
                WHERE I.consumer_id = %s AND I.restaurant_id = %s
                """.format(table_name=cls.__image_consumer_restaurant_table_name__),
                row[0], row[1]
            ).fetchall()

            for img_row in review_img_query_rows:
                img_result = db_conn.execute(
                    """
                    SELECT url
                    FROM {table_name} AS I
                    WHERE I.image_id = %s
                    """.format(table_name=cls.__image_table_name__),
                    img_row[0]
                ).fetchone()

                review_result[-1]["image_urls"].append(img_result[0])

        return review_result

    @classmethod
    def getRestaurantAttributes(cls, db_conn, restaurant_id):

        query_row = db_conn.execute(
            """SELECT *
            FROM {table_name_1} AS R, {table_name_2} AS A,
            {table_name_3} AS CR, {table_name_4} AS C,
            {table_name_5} AS HR, {table_name_6} AS H
            WHERE R.restaurant_id=%s
                AND R.zipcode = A.zipcode
                AND CR.restaurant_id = R.restaurant_id
                AND C.cuisine_id = CR.cuisine_id
                AND HR.restaurant_id = R.restaurant_id
                AND H.hashtag_id = HR.hashtag_id
            """.format(
                table_name_1=cls.__restaurant_table_name__,
                table_name_2=cls.__area_table_name__,
                table_name_3=cls.__cuisinesrestaurantsrelationship_table_name__,
                table_name_4=cls.__cuisines_table_name__,
                table_name_5=cls.__hashtagsconsumersrestaurantsrelationship_table_name__,
                table_name_6=cls.__hashtags_table_name__
            ),
            restaurant_id
        ).fetchone()


        schema = table_schema.restaurant_schema + table_schema.area_schema + \
            table_schema.cuisine_restaurant_relationship_schema + \
            table_schema.cuisine_schema + \
            table_schema.hashtag_consumer_restaurant_relationship_schema + \
            table_schema.hashtag_schema

        restaurant = dict(
            zip(schema, query_row))

        return restaurant
