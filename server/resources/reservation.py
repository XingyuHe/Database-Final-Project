from flask_restful import Resource
from flask import abort, session, request,  make_response, render_template
from marshmallow import Schema, fields

from db import db_engine, table_schema


class ReservationQuerySchema(Schema):
    party_size = fields.Int(required=True)
    party_time = fields.Str(required=True)


reservationQuerySchema = ReservationQuerySchema()


class Reservation(Resource):

    __restaurant_table_name__ = "RESTAURANTS"
    __area_table_name__ = "AREAS"

    def get(self, restaurant_id):

        if 'username' not in session:
            return  make_response(render_template("please_login.html"), 200, {'Content-Type': 'text/html'})

        restaurant_found = self.find_restaurant(restaurant_id)

        print("restaurant {restaurant_id} found: {restaurant}".format(
            restaurant_id=restaurant_id, restaurant=restaurant_found))

        return make_response(render_template("reservation.html", data=restaurant_found), 200, {'Content-Type': 'text/html'})

    def post(self, restaurant_id):

        if 'username' not in session:
            return  "Please login first."

        consumer_id = session['consumer_id']
        errors = reservationQuerySchema.validate(request.form)
        if errors:
            print(str(errors))
            abort(400, str(errors))

        result = self.make_reservation(
            consumer_id, restaurant_id, request.form)

        if result:
            return make_response(render_template("reservation_success.html"), 200, {'Content-Type': 'text/html'})
        else:
            return f"failed to make a reservation"

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
            table_name_1=cls.__restaurant_table_name__,
            table_name_2=cls.__area_table_name__
        )

        result = db_conn.execute(query, restaurant_id)
        restaurant = result.fetchone()
        print("restaurant: ", restaurant)
        if restaurant:
            restaurant = dict(
                zip(table_schema.restaurant_schema + table_schema.area_schema, restaurant))
        db_conn.close()
        return restaurant

    @classmethod
    def make_reservation(cls, consumer_id, restaurant_id, form):
        try:
            db_conn = db_engine.connect()
        except:
            print("failed to connect to database")
            abort(500, "<p>Database Error</p>")

        insert_query = """
        INSERT INTO Reservations (consumer_id, restaurant_id, party_size, party_time)
        VALUES (%s, %s, %s, %s)
        """

        try:
            result = db_conn.execute(
                insert_query,
                consumer_id, restaurant_id, form['party_size'], form['party_time']
            )
        except:
            abort(500, "Reservation failed")

        search_query = """
        SELECT *
        FROM Reservations
        WHERE consumer_id=%s AND restaurant_id=%s AND party_size=%s AND party_time=%s
        """

        try:
            result = db_conn.execute(
                search_query,
                consumer_id, restaurant_id, form['party_size'], form['party_time']
            )
        except:
            abort(500, "Reservation failed")

        row = result.fetchone()

        db_conn.close()

        if row:
            print("successfully made reservation to database: ", row)
            return row
        else:
            return None
