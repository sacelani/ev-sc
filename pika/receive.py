#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='127.0.0.1'))
channel = connection.channel()
channel.queue_delete(queue='hello')
channel.queue_declare(queue='hello')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(queue='hello', consumer_callback = callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
