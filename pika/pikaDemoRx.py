import pika
import matplotlib.pyplot as plt

x = []
y = []

params = pika.ConnectionParameters(
    host='amqp://msprqdua:XO-wSDRahPG_y2HHwzLlP80B0NiB31h-@wombat.rmq.cloudamqp.com/msprqdua',  # fill this in
    port=5672,
    virtual_host='/',
    socket_timeout=None)

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.exchange_declare(exchange='test',
                         exchange_type='topic')
# auto_delete = True)

q = channel.queue_declare(exclusive=True)

channel.queue_bind(exchange='test',
                   queue=q.method.queue,
                   routing_key='ev-sc')


def callback(ch, method, properties, body):
    #    print(body)
    data = str(body).split(',')

    x.append(int(data[0][-1]))
    y.append(int(data[1][-2]))

    plt.scatter(x, y, c='green', marker='o')
    plt.show(block=False)

    plt.pause(0.0001)


channel.basic_consume(callback,
                      queue=q.method.queue,
                      no_ack=True)

channel.start_consuming()
