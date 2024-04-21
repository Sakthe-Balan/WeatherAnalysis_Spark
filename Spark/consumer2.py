from confluent_kafka import Consumer, KafkaError
import json

def basic_consumer(bootstrap_servers='localhost:9092', group_id='my_consumer_group', topic='weather_data_batch'):
    conf = {
        'bootstrap.servers': bootstrap_servers,
        'group.id': group_id,
        
    }

    consumer = Consumer(conf)
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition, consumer reached end of log
                    continue
                else:
                    print(msg.error())
                    break

            # Process the message
            data = json.loads(msg.value().decode('utf-8'))
            print("Received message:", data)

    except KeyboardInterrupt:
        pass

    finally:
        consumer.close()

# Example usage
basic_consumer()
