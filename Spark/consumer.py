from confluent_kafka import Consumer, KafkaError
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from datetime import datetime

def kafka_consumer(group_id, bootstrap_servers='localhost:9092'):
    # Configure the consumer
    conf = {'bootstrap.servers': bootstrap_servers, 'group.id': group_id}
    min_values = {'Temperature (C)': 110, 'Humidity': 110, 'Wind Speed (km/h)': 110,
                  'Wind Bearing (degrees)': 110, 'Visibility (km)': 110, 'Loud Cover': 110, 'Pressure (millibars)': 110}
    max_values = {'Temperature (C)': -1, 'Humidity': -1, 'Wind Speed (km/h)': -1,
                  'Wind Bearing (degrees)': -1, 'Visibility (km)': -1, 'Loud Cover': -1, 'Pressure (millibars)': -1}
    sum_values = {'Temperature (C)': 0, 'Humidity': 0, 'Wind Speed (km/h)': 0,
                  'Wind Bearing (degrees)': 0, 'Visibility (km)': 0, 'Loud Cover': 0, 'Pressure (millibars)': 0}
    count_values = {'Temperature (C)': 0, 'Humidity': 0, 'Wind Speed (km/h)': 0,
                    'Wind Bearing (degrees)': 0, 'Visibility (km)': 0, 'Loud Cover': 0, 'Pressure (millibars)': 0}

    # Create the consumer
    consumer = Consumer(conf)

    # Subscribe to the topic
    consumer.subscribe(['weather_read'])

    # Create a Spark session
    spark = SparkSession.builder \
        .appName("KafkaStreamingDemo") \
        .getOrCreate()

    # Define the schema for the incoming JSON messages
    schema = StructType([
        StructField("Formatted Date", StringType()),
        StructField("Summary", StringType()),
        StructField("Precip Type", StringType()),
        StructField("Temperature (C)", DoubleType()),
        StructField("Humidity", DoubleType()),
        StructField("Wind Speed (km/h)", DoubleType()),
        StructField("Wind Bearing (degrees)", DoubleType()),
        StructField("Visibility (km)", DoubleType()),
        StructField("Loud Cover", DoubleType()),
        StructField("Pressure (millibars)", DoubleType()),
        StructField("Daily Summary", StringType())
    ])

    # Open a text file for writing
    output_file = open("min_max_avg_values.txt", "w")

    try:
        while True:
            # Poll for messages
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition
                    continue
                else:
                    # Error
                    print("Consumer error:", msg.error())
                    break

            # Convert the message value to JSON
            json_data = msg.value().decode('utf-8')

            # Convert JSON to DataFrame
            json_df = spark.read.json(spark.sparkContext.parallelize([json_data]), schema)

            # Extract necessary columns for processing
            numerical_columns = ['Temperature (C)', 'Humidity', 'Wind Speed (km/h)',
                                 'Wind Bearing (degrees)', 'Visibility (km)', 'Loud Cover', 'Pressure (millibars)']
            processed_df = json_df.select(*numerical_columns)

            # Iterate through each row to find min, max, sum, and count values for each numerical column
            for row in processed_df.collect():
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for column in numerical_columns:
                    value = row[column]
                    min_values[column] = min(min_values[column], value)
                    max_values[column] = max(max_values[column], value)
                    sum_values[column] += value
                    count_values[column] += 1

            # Calculate averages
            avg_values = {key: sum_values[key] / count_values[key] if count_values[key] != 0 else None for key in sum_values}

            # Write to the output file
            output_file.write(f"{current_time} - Min/Max/Avg Values:\n")
            for column in numerical_columns:
                output_file.write(f"{column}: Min={min_values[column]}, Max={max_values[column]}, Avg={avg_values[column]}\n")

    finally:
        # Close the consumer
        consumer.close()
        # Close the output file
        output_file.close()

# Example usage
if __name__ == "__main__":
    kafka_consumer('Weather')
