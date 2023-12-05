import time
import pika
import logging
import threading


def send_message(queue: str, message: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange="", routing_key=queue, body=message)
    logging.debug(f"Sent message to queue {queue}: {message}")
    connection.close()


def callback(ch, method, properties, body):
    message = body.decode("utf-8")
    logging.debug(f"Received message: {message}")


def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.queue_declare(queue="hello")
    channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    logging.debug("Started consuming messages")


def create_consumer_thread():
    time.sleep(10)  # Wait for RabbitMQ to start
    threading.Thread(target=consume, daemon=True).start()
