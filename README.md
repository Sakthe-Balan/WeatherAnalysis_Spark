# Real-Time Weather Analysis with Stream and Batch Processing



![Arch](https://github.com/Sakthe-Balan/WeatherAnalysis_Spark/assets/103580234/229ec5dd-7769-4176-b22f-07ab022f93ed)


## Overview

This project aims to perform real-time weather analysis using stream and batch processing techniques. It involves ingesting weather data from a CSV file, streaming it to Apache Kafka, storing it in MySQL, and then processing it using Apache Spark. The analysis includes finding the minimum, maximum, and average values of various weather parameters.

## Data Description

The CSV file contains the following columns:

1. Formatted Date
2. Summary
3. Precip Type
4. Temperature (C)
5. Apparent Temperature (C)
6. Humidity
7. Wind Speed (km/h)
8. Wind Bearing (degrees)
9. Visibility (km)
10. Loud Cover
11. Pressure (millibars)
12. Daily Summary

## Project Architecture

This project's architecture includes the following components:

- **Producer (Stream)**: Reads the weather data from the CSV file and produces it to Apache Kafka.
- **Apache Kafka**: Acts as a message broker, receiving weather data from the producer and making it available to consumers.
- **MySQL Database**: Stores the weather data for both real-time and batch processing.
- **Consumer (Stream)**: Subscribes to the Kafka topic and performs real-time processing of the weather data using Apache Spark Streaming.
- **Consumer (Batch)**: Retrieves data from the MySQL database and conducts batch processing using Apache Spark.
- **Producer (Batch)**: Reads weather data from the MySQL database and produces it to a Kafka topic for further analysis.

## Conceptual Workflow

1. **Data Ingestion**: The producer (stream) reads weather data from the CSV file and produces it to a Kafka topic.
2. **Streaming Data Processing**: The streaming consumer subscribes to the Kafka topic, processes incoming data using Apache Spark Streaming, and computes real-time metrics such as minimum, maximum, and average values.
3. **Data Storage**: The processed data is stored in the MySQL database for future reference and batch processing.
4. **Batch Processing (Producer)**: The producer (batch) retrieves weather data from the MySQL database and produces it to a Kafka topic.
5. **Batch Processing (Consumer)**: The batch consumer retrieves data from the Kafka topic, conducts batch processing using Apache Spark, and computes metrics similar to the streaming process.
6. **Comparison**: The results from both streaming and batch processing are compared to determine which approach yields better insights or performance.

### Instructions to Run the Application

1. **Start Kafka and Spark Servers:**
   - Run `docker-compose up` command to start Kafka and Spark servers.

2. **Push Data to Database and Kafka Stream:**
   - Run `producer.py` script to push data to your database and Kafka stream.

3. **Receive Kafka Stream and Calculate Metrics:**
   - Run `consumer.py` script to receive the stream from Kafka.
   - Consumer script will calculate the minimum, maximum, and average for the received data and put it into a text file.

4. **Run Batch Producer:**
   - Run `batch_producer.py` script to pull data from the database in batches of 10 and send it to Kafka.

5. **Process Batched Data and Store in Text File:**
   - Run `consumer2.py` script to process the batched data received from Kafka.
   - Consumer2 script will put the processed data into a text file.

6. **Comparison:**
   - Compare the text files generated by `consumer.py` and `consumer2.py` for speed and accuracy.



## System Design Considerations

- **Scalability**: The system is designed to scale horizontally to handle increasing data volumes.
- **Reliability**: Measures are implemented to ensure high availability and fault tolerance.
- **Efficiency**: Optimization techniques are applied to minimize latency and maximize throughput in both streaming and batch processing.

## Potential Challenges

- **Data Consistency**: Ensuring consistency between real-time and batch-processed data can be challenging due to the asynchronous nature of stream processing.
- **Performance Tuning**: Fine-tuning the system for optimal performance, especially when dealing with large datasets, requires careful consideration.
- **Resource Management**: Efficient utilization of computational resources is essential to prevent bottlenecks and ensure smooth operation of the system.

## Conclusion

This project demonstrates the effectiveness of combining stream and batch processing techniques for real-time weather analysis. By comparing the results of both approaches, we can gain valuable insights into the performance and suitability of each method for different use cases.

## Acknowledgments

- Special thanks to the open-source community for providing the tools and frameworks used in this project.
- Acknowledgment to team members and advisors for their support and contributions throughout the development process.
