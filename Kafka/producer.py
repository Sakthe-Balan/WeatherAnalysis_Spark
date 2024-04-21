import csv
import time
from confluent_kafka import Producer

def delivery_report(err, msg):
    if err is not None:
        print("Message delivery failed:", err)
    else:
        print("Message delivered to", msg.topic(), "partition", msg.partition())

def kafka_producer(filename, bootstrap_servers='localhost:9092'):
    # Configure the producer
    conf = {'bootstrap.servers': bootstrap_servers}

    # Create the producer
    producer = Producer(conf)

    # Read the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            # Send each row as a message
            producer.produce('weather_read', value=','.join(row).encode('utf-8'), callback=delivery_report)
            # Introduce a delay between producing messages (optional)
            time.sleep(0.5)

    # Flush the producer to ensure all messages are delivered
    producer.flush()

    # Close the producer
    producer.close()

# Example usage
kafka_producer('weatherHistory.csv')
