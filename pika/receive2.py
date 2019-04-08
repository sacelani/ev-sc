#example_consumer.py
import pika, os, time

# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = os.environ.get('CLOUDAMQP_URL', 'amqp://msprqdua:XO-wSDRahPG_y2HHwzLlP80B0NiB31h-@wombat.rmq.cloudamqp.com/msprqdua')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel
channel.queue_delete(queue='hello')  # Delete Queue 
channel.queue_declare(queue='hello') # Declare a queue

# create a function which is called on incoming messages
def callback(ch, method, properties, body):
	print("Received: %r" % body)

# set up subscription on the queue
channel.basic_consume(consumer_callback = callback, queue='hello')

# start consuming (blocks)
print("Waiting for messages.   Press CRTL+C to exit.")
channel.start_consuming()
