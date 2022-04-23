from flask_restful import Resource
from flask import request, abort, make_response, render_template, session

from db import db_engine, table_schema


class MyReservation(Resource):

    __restaurants_table_name__ = "Restaurants"
    __reservations_table_name__ = "Reservations"

    def get(self):

        if 'username' not in session:
            return make_response(
                render_template("please_login.html"), 200, {'Content-Type': 'text/html'})

        reservations_found = self.find_reservations(session['consumer_id'])
        print(len(reservations_found))
        if reservations_found:
            return make_response(
                render_template(
                    "reservations_found.html",
                    data=reservations_found),
                200, {'Content-Type': 'text/html'})

        return "No reservations found"

    @classmethod
    def find_reservations(cls, consumer_id):
        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        query = """
        SELECT DISTINCT *
        FROM {table_name_1} AS RV, {table_name_2} AS R
        WHERE RV.consumer_id = %s AND R.restaurant_id = RV.restaurant_id
        """.format(
            table_name_1=cls.__reservations_table_name__,
            table_name_2=cls.__restaurants_table_name__,
        )

        result = db_conn.execute(
            query, consumer_id)
        reservations_rows = result.fetchall()

        search_results = []
        if reservations_rows:
            for row in reservations_rows:
                reservation = dict(zip(table_schema.reservation_schema + table_schema.restaurant_schema, row))
                search_results.append(reservation)

        db_conn.close()
        return search_results
