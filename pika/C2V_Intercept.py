"""

Author: Sam Celani

File:   C2V_Intercept.py

Description:

    This script listens to wireless communications sent from the cloud (mobile lab)
    to the vehicle.

    It is part of the ARPA-E Project: NEXTCAR.


Imported Files:

    configInit.py

        Helps to determine where the script should be listening.
    
"""


###########################################################

#
#   IMPORTS
#       All imports are nested in a try-except block
#       to avoid fatal errors, or at least to simply
#       put them off for a little bit.
#

try:
    
    import configInit   ##  Used to decide server
    import datetime     ##  Used in file naming
    import pika         ##  Used in data transmission
    import sys          ##  Used for testing

except Exception as ex:
    print ex
    exit()

###########################################################

#
#   INITIALIZE VARIABLES
#

##  Keeping this for defaulting, in case configInit fails

SERVERIP =      ['141.219.181.216', 'Kuilin']
SERVERIP =      ['166.152.103.250', 'Mobile Lab']
credA =         'aps-lab'
credB =         'aps-lab'
CREDENTIALS =   pika.PlainCredentials(credA, credB)
LOGNAME =       'cacc_test_exchange'
ROUTING_KEY =   'cloud_cacc'

params = None

###########################################################

#
#   USE OF CONFIGINIT
#

try:
    # kuilin, beta, sam, mobile_lab, tony_url
    datum = configInit.init('tony_url')
    SERVERIP = datum[0]
    if len(datum) is 3:
        LOGNAME = datum[1]
        ROUTING_KEY = datum[2]
        params = pika.URLParameters(SERVERIP)
        
        print SERVERIP
        print LOGNAME
        print ROUTING_KEY
        print '\n'
        
    elif len(datum) is 4:
        credA = datum[1][0]
        credB = datum[1][1]
        if not datum[1][0] is None:
            CREDENTIALS = pika.PlainCredentials(credA,credB)
        else:
            CREDENTIALS = None
        LOGNAME = datum[2]
        ROUTING_KEY = datum[3]
        params = pika.ConnectionParameters(host = SERVERIP,
                                           port = 5672,
                                           virtual_host = '/',
                                           credentials = CREDENTIALS)
                                           
        print SERVERIP
        print '({0}, {1})'.format(credA, credB)
        print LOGNAME
        print ROUTING_KEY
        print '\n'
        
    else:
        # shouldn't even be possible
        print 'What?'
except:
    print 'Proceeding with default connection information:\n'
    params = pika.ConnectionParameters(host = SERVERIP,
                                       port = 5672,
                                       virtual_host = '/',
                                       credentials = CREDENTIALS)

    print SERVERIP
    print '({0}, {1})'.format(credA, credB)
    print LOGNAME
    print ROUTING_KEY
    print '\n'

##  Create a connection
connection = pika.BlockingConnection(params)

##  Create a channel
channel = connection.channel()

##  Declare exhange
channel.exchange_declare(exchange = LOGNAME,
                         exchange_type = 'topic',
                         auto_delete = True)
##  Declare queue
q = channel.queue_declare(exclusive = True)

##  Bind queue to exchange
channel.queue_bind(exchange = LOGNAME,
                   queue = q.method.queue,
                   routing_key = ROUTING_KEY)

print ' [*] Waiting for packets...'

##  Define a consumption
channel.basic_consume(callback,
                      queue = q.method.queue,
                      no_ack = True)

##  Acutal consumption
try:                            ##  Consumption is nested in a try-
    channel.start_consuming()   ##  xcept block, in the hopes that it
except KeyboardInterrupt:       ##  handles a KeyboardInterrupt gracefully. 
    exit()                      ##  Spoiler Alert:: It doesn't work very well

###########################################################

#
#   FUNCTION DEFINITION 1
#       Basic Callback function for StartConsumer.py
#           This is what happens when data is received

def callback(ch, method, properties, body):

    filename = getTheDate()             ##  Create file to dump data

    print ' [x] {}\n\n'.format(body)    ##  Print to console

    with open(filename,'w') as file:    ##  Open file specificed
        file.write(sanitizedBody)       ##  Write data to file

###########################################################

#
#   FUNCTION DEFINITION 2
#       Basic Callback function for email exchange
#           This is what happens when data is received

def getTheDate():

    timestamp = str(datetime.datetime.now())    # Get time, convert to usable string    --> YYYY-Mo-DD HH:Mi:SS.Millisecond
    timestamp = timestamp.split('.')[0]         # Drop milliseconds                     --> YYYY-Mo-DD HH:Mi:SS
    timestamp = timestamp.replace(' ','_')      # Replace space with underscore         --> YYYY-Mo-DD_HH:Mi:SS
    timestamp = timestamp.replace(':','h',1)    # Replace colon with 'h' for hours      --> YYYY-Mo-DD_HHhMi:SS
    timestamp = timestamp.replace(':','m',1)    # Replace colon with 'm' for minutes    --> YYYY-Mo-DD_HHhMimSS
    timestamp = timestamp + 's'                 # Append 's' for seconds                --> YYYY-Mo-DD_HHhMimSSs

    return 'RabbitMq_Rx_' + timestamp + '.txt'  # Create filename

###########################################################

