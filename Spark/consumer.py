from confluent_kafka import Consumer, KafkaError

def kafka_consumer(group_id, bootstrap_servers='localhost:9092'):
    # Configure the consumer
    conf = {'bootstrap.servers': bootstrap_servers, 'group.id': group_id}

    # Create the consumer
    consumer = Consumer(conf)

    # Subscribe to the topic
    consumer.subscribe(['weather_read'])

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

            # Print the received message
            
            print('Received message value: {}'.format(msg.value().decode('utf-8')))

    finally:
        # Close the consumer
        consumer.close()

# Example usage
kafka_consumer('Weather')
