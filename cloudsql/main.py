import os
import pandas as pd
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector

load_dotenv()

connector = Connector()

# build connection for db using Python Connector
def getconn():
    conn = connector.connect(
        instance_connection_string=os.environ['INSTANCE_CONNECTION_NAME'],
        driver="pg8000",
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        db=os.environ['DB_NAME'],
    )
    return conn

pool = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)


def db_connection_test():
    with pool.connect() as conn:
        current_time = conn.execute(text("SELECT NOW()")).fetchone()
        print(f"Time: {str(current_time[0])}")

def load_data_to_db():
    with pool.connect() as conn:
        cols = [
            (20, 51),    # Name
            (72, 75),    # Station
            (106, 116),  # Latitude
            (116, 127)   # Longitude
        ]
        df = pd.read_fwf(r"https://www.ncei.noaa.gov/access/homr/file/nexrad-stations.txt", colspecs=cols, skiprows=[1])
        df.to_sql(name='noaa_tbl', con=conn, index=False, if_exists='replace')
        print("Done")

def fetch_data_from_db():
    with pool.connect() as conn:
        df = pd.read_sql_table("noaa_tbl", con=conn)
        print(df.head(10))

def delete_table_from_db():
    with pool.connect() as conn:
        conn.execute("DROP TABLE IF EXISTS noaa_tbl")
        print("Table deleted")


print(f"-----Testing connection to Cloud SQL instance-----")
db_connection_test()

print(f"-----Loading data to Cloud SQL instance-----")
load_data_to_db()

print("-----Get data from Cloud SQL instance-----")
fetch_data_from_db()

print("-----delete data from Cloud SQL instance-----")
delete_table_from_db()