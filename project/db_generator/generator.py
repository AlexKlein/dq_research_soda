import os
import psycopg2
from sqlalchemy.engine.url import make_url
from datetime import date, timedelta
import random


def create_database_connection():
    """Create a connection to the PostgreSQL database using an environment variable."""

    # Fetch the connection string from the environment variable
    conn_str = os.environ.get("MY_SMALL_DWH_SQL_ALCHEMY_CONN")
    if not conn_str:
        raise ValueError("Environment variable MY_SMALL_DWH_SQL_ALCHEMY_CONN not found!")

    # Parse the connection string
    url = make_url(conn_str)

    conn = psycopg2.connect(
        dbname=url.database,
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port
    )
    return conn


def create_database_connection():
    """Create a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='postgres',
        host='my_small_dwh',
        port=5432
    )
    return conn


def setup_database(cur):
    """Create the necessary schema and table in the database."""
    cur.execute('''
        CREATE SCHEMA IF NOT EXISTS automotive;
    ''')

    cur.execute('''
        DROP TABLE IF EXISTS automotive.cars;
        CREATE TABLE automotive.cars (
            id SERIAL PRIMARY KEY,
            model VARCHAR(50),
            manufacture_date DATE,
            price NUMERIC(10,2),
            is_electric BOOLEAN,
            color VARCHAR(20),
            engine_power NUMERIC(5,2)
        );
    ''')


def insert_sample_data(cur):
    """Insert sample data into the cars table."""
    models = ['Tesla Model 3', 'Toyota Corolla', 'Ford Focus', 'BMW M3', 'Audi A4']
    colors = ['Red', 'Blue', 'Green', 'White', 'Black']

    for _ in range(23):
        model = random.choice(models)
        m_date = date.today() - timedelta(days=random.randint(0, 365*5))  # cars from the last 5 years
        price = round(random.uniform(20000, 100000), 2)
        is_electric = model.startswith('Tesla')
        color = random.choice(colors)
        engine_power = round(random.uniform(100, 400), 2)  # 100 to 400 HP

        cur.execute('''
            INSERT INTO automotive.cars (model, manufacture_date, price, is_electric, color, engine_power)
            VALUES (%s, %s, %s, %s, %s, %s);
        ''', (model, m_date, price, is_electric, color, engine_power))


def start_generation():
    """Main function to generate the sample data in the database."""
    conn = create_database_connection()
    cur = conn.cursor()

    setup_database(cur)
    insert_sample_data(cur)

    conn.commit()
    cur.close()
    conn.close()
