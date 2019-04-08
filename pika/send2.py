#example_publisher.py
import pika, os, logging
logging.basicConfig()

# Parse CLODUAMQP_URL (fallback to localhost)
url = os.environ.get('CLOUDAMQP_URL', 'amqp://msprqdua:XO-wSDRahPG_y2HHwzLlP80B0NiB31h-@wombat.rmq.cloudamqp.com/msprqdua')
params = pika.URLParameters(url)
params.socket_timeout = 5

connection = pika.BlockingConnection(params) # Connect to CloudAMQP
channel = connection.channel() # start a channel
channel.queue_declare(queue='hello') # Declare a queue
# send a message

channel.basic_publish(exchange='', routing_key='hello', body='Mike was here')
print ("[x] Message sent to consumer")
connection.close()
