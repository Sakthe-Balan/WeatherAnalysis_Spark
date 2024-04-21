import csv
import time
from confluent_kafka import Producer
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

def delivery_report(err, msg):
    if err is not None:
        print("Message delivery failed:", err)
    else:
        print("Message delivered to", msg.topic(), "partition", msg.partition())

def get_mysql_config_from_env():
    return {
        'user': os.environ.get('MYSQL_USER'),
        'password': os.environ.get('MYSQL_PASSWORD'),
        'host': os.environ.get('MYSQL_HOST'),
        'database': os.environ.get('MYSQL_DATABASE')
    }

def create_table_if_not_exists(cursor):
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS weather_data (
            `Formatted Date` VARCHAR(255),
            Summary VARCHAR(255),
            `Precip Type` VARCHAR(255),
            `Temperature (C)` FLOAT,
            `Apparent Temperature (C)` FLOAT,
            Humidity FLOAT,
            `Wind Speed (km/h)` FLOAT,
            `Wind Bearing (degrees)` FLOAT,
            `Visibility (km)` FLOAT,
            `Loud Cover` FLOAT,
            `Pressure (millibars)` FLOAT,
            `Daily Summary` VARCHAR(255)
        )
    """)

def truncate_table(cursor):
    cursor.execute("TRUNCATE TABLE weather_data")

def kafka_producer_with_mysql(filename, bootstrap_servers='localhost:9092'):
    mysql_config = get_mysql_config_from_env()
    # Configure the Kafka producer
    kafka_conf = {'bootstrap.servers': bootstrap_servers}
    producer = Producer(kafka_conf)

    # Configure MySQL connection
    mysql_conn = mysql.connector.connect(**mysql_config)
    mysql_cursor = mysql_conn.cursor()

    # Create table if not exists
    create_table_if_not_exists(mysql_cursor)

    # Truncate table
    truncate_table(mysql_cursor)

    # Read the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
           # Prepare data as a dictionary
            data = {
                'Formatted Date': datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f %z').isoformat(),
                'Summary': row[1],
                'Precip Type': row[2],
                'Temperature (C)': float(row[3]),
                'Apparent Temperature (C)': float(row[4]),
                'Humidity': float(row[5]),
                'Wind Speed (km/h)': float(row[6]),
                'Wind Bearing (degrees)': float(row[7]),
                'Visibility (km)': float(row[8]),
                'Loud Cover': float(row[9]),
                'Pressure (millibars)': float(row[10]),
                'Daily Summary': row[11]
            }

            # Send data to Kafka as JSON
            producer.produce('weather_read', value=json.dumps(data).encode('utf-8'), callback=delivery_report)

            # Insert into MySQL table
            try:
                mysql_cursor.execute(""" 
                    INSERT INTO weather.weather_data (`Formatted Date`, Summary, `Precip Type`, `Temperature (C)`, `Apparent Temperature (C)`, Humidity, `Wind Speed (km/h)`, `Wind Bearing (degrees)`, `Visibility (km)`, `Loud Cover`, `Pressure (millibars)`, `Daily Summary`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f %z'), row[1], row[2], float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7]), float(row[8]), float(row[9]), float(row[10]), row[11]))
                print("Row inserted successfully:", row)
                mysql_conn.commit()
            except Exception as e:
                print("Error inserting row:", e)

            # Introduce a delay between producing messages (optional)
            time.sleep(0.5)

    # Flush the Kafka producer to ensure all messages are delivered
    producer.flush()

    # Commit MySQL transaction
    mysql_conn.commit()

    # Close connections
    producer.close()
    mysql_cursor.close()
    mysql_conn.close()

# Example usage
kafka_producer_with_mysql('weatherHistory.csv')