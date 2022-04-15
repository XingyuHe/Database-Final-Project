from sqlalchemy import create_engine
import os

# DATABASEURI = "postgresql://xh2513:xh2513@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2"
print(os.environ.get('MYDB_PASSWORD'))
DATABASEURI = f"postgresql://postgres:{os.environ.get('MYDB_PASSWORD')}@database-4111.ce1y1qbvwlr2.us-east-1.rds.amazonaws.com:5432/mydb"
db_engine = create_engine(DATABASEURI, connect_args={'connect_timeout': 5})


class TableSchema:
    schema_query = """
    SELECT column_name, ordinal_position
    FROM INFORMATION_SCHEMA.COLUMNS
    where table_name='{table_name}'
    ORDER BY ordinal_position;
    """

    def __init__(self):
        db_conn = db_engine.connect()
        self.restaurant_schema = self.get_schema('restaurants')
        self.area_schema = self.get_schema('areas')
        self.cuisine_schema = self.get_schema('cuisines')
        self.cuisine_restaurant_relationship_schema = self.get_schema('cuisinesrestaurantsrelationship')
        self.hashtag_consumer_restaurant_relationship_schema = self.get_schema('hashtagsconsumersrestaurantsrelationship')
        self.hashtag_schema = self.get_schema('hashtags')
        db_conn.close()

    @classmethod
    def get_schema(cls, db_conn, table_name):
        print("getting schema")
        while True:
            try:
                db_conn = db_engine.connect()
                result = db_conn.execute(cls.schema_query.format(table_name=table_name))
                schema_rows = result.fetchall()
                schema = []
                for row in schema_rows:
                    schema.append(row[0])
                db_conn.close()
                print(table_name+" schema: ", schema)
                break
            except:
                print("timed out, trying again")
                pass

        return schema

table_schema = TableSchema()


    