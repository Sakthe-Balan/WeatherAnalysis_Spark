# from confluent_kafka import Consumer, KafkaError
# import json

# def basic_consumer(bootstrap_servers='localhost:9092', group_id='my_consumer_group', topic='weather_data_batch'):
#     conf = {
#         'bootstrap.servers': bootstrap_servers,
#         'group.id': group_id,
        
#     }

#     consumer = Consumer(conf)
#     consumer.subscribe([topic])

#     try:
#         while True:
#             msg = consumer.poll(1.0)
#             if msg is None:
#                 continue
#             if msg.error():
#                 if msg.error().code() == KafkaError._PARTITION_EOF:
#                     # End of partition, consumer reached end of log
#                     continue
#                 else:
#                     print(msg.error())
#                     break

#             # Process the message
#             data = json.loads(msg.value().decode('utf-8'))
#             print("Received message:", data)

#     except KeyboardInterrupt:
#         pass

#     finally:
#         consumer.close()

# # Example usage
# basic_consumer()

from confluent_kafka import Consumer, KafkaError
from datetime import datetime
import json

def kafka_batch_consumer(group_id, bootstrap_servers='localhost:9092', output_file='min_max_avg_values1.txt'):
    # Configure the consumer
    conf = {'bootstrap.servers': bootstrap_servers, 'group.id': group_id}
    
    # Create the consumer
    consumer = Consumer(conf)

    # Subscribe to the topic
    consumer.subscribe(['weather_data_batch'])

    # Initialize dictionaries for storing min, max, sum, and count values
    min_values = {'Temperature (C)': 110, 'Humidity': 110, 'Wind Speed (km/h)': 110,
                  'Wind Bearing (degrees)': 110, 'Visibility (km)': 110, 'Loud Cover': 110, 'Pressure (millibars)': 110}
    max_values = {'Temperature (C)': -1, 'Humidity': -1, 'Wind Speed (km/h)': -1,
                  'Wind Bearing (degrees)': -1, 'Visibility (km)': -1, 'Loud Cover': -1, 'Pressure (millibars)': -1}
    sum_values = {'Temperature (C)': 0, 'Humidity': 0, 'Wind Speed (km/h)': 0,
                  'Wind Bearing (degrees)': 0, 'Visibility (km)': 0, 'Loud Cover': 0, 'Pressure (millibars)': 0}
    count_values = {'Temperature (C)': 0, 'Humidity': 0, 'Wind Speed (km/h)': 0,
                    'Wind Bearing (degrees)': 0, 'Visibility (km)': 0, 'Loud Cover': 0, 'Pressure (millibars)': 0}

    try:
        with open(output_file, 'a') as file:
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

                # Convert JSON to list of dictionaries
                batch_data = json.loads(json_data)
                print(batch_data)
                # Iterate through each record in the batch
                for record in batch_data:
                    # Iterate through each numerical column in the record
                    for column in record:
                        if column in min_values:
                            value = record[column]
                            # Update min, max, sum, and count values
                            min_values[column] = min(min_values[column], value)
                            max_values[column] = max(max_values[column], value)
                            sum_values[column] += value
                            count_values[column] += 1

                # Calculate averages
                avg_values = {key: sum_values[key] / count_values[key] if count_values[key] != 0 else None for key in sum_values}

                # Write to the output file
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"{current_time} - Min/Max/Avg Values:\n")
                for column in min_values:
                    file.write(f"{column}: Min={min_values[column]}, Max={max_values[column]}, Avg={avg_values[column]}\n")
                file.write("\n")

    finally:
        # Close the consumer
        consumer.close()

# Example usage
if __name__ == "__main__":
    kafka_batch_consumer('WeatherBatch', output_file='min_max_avg_values1.txt')
