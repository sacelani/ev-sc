import pika
import random


params = pika.ConnectionParameters(host = '127.0.0.1',   # fill this in
                                   port = 5672,
                                   virtual_host = '/',
                                   socket_timeout = None)

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.exchange_declare(exchange = 'test',
                         exchange_type = 'topic')
                         # auto_delete = True)

q = channel.queue_declare(exclusive = True)

channel.queue_bind(exchange = 'test',
                   queue = q.method.queue,
                   routing_key = 'ev-sc')



for c in range(10):
    first = random.randint(0, 10)
    second = random.randint(0, 10)

    mess = str(first) + ', ' + str(second)

    channel.basic_publish(exchange = 'test',
                          routing_key = 'ev-sc',
                          body = mess)


