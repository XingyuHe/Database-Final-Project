from sqlalchemy import create_engine

DATABASEURI = "postgresql://xh2513:xh2513@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2"

db_engine = create_engine(DATABASEURI)