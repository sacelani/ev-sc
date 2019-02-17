"""

Author: Sam Celani

File:   C2V_Producer.py

Description:

    This file sends a predefined data packet every five seconds.
    The receiver of the message is determined by the argument
    passed to configInit.py
    
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

    import configInit       ##  Used to decide server
    import pika             ##  Used in data transmission
    import struct           ##  Used in data packing
    import time             ##  Used for sleep function
    
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
    datum = configInit.init('mobile_lab')
    SERVERIP = datum[0]
    if len(datum) is 3:
        ROUTING_KEY = datum[1]
        LOGNAME = datum[2]
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
        ROUTING_KEY = datum[2]
        LOGNAME = datum[3]
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

###########################################################

#
#   CONNECTION
#

##  Declare connection based off of params variables
connection = pika.BlockingConnection(params)

##  Make channel from connection
channel = connection.channel()

##  Declare exchange
channel.exchange_declare(exchange = LOGNAME,
                         exchange_type = 'topic')

##  Declare queue
q = channel.queue_declare(exclusive = True)

##  Bind queue to exchange over routing key
channel.queue_bind(exchange = LOGNAME,
                   queue = q.method.queue,
                   routing_key = ROUTING_KEY)

while True:

    ##  Define a message to match the ME data packet
    message = struct.pack('!id',
                          55,
                          0.2)

    ##  Define a message to match the CE data packet
    message = struct.pack('!Hdddiiddddddddddidd',
                          123,
                          0.1,
                          1.6,
                          5,
                          16,
                          5,
                          35,
                          35,
                          35,
                          35,
                          35,
                          25,
                          25,
                          25,
                          25,
                          25,
                          1,
                          2.5,
                          35)
    
    try:
        ##  Publish a message to the exchange LOGNAME using the routing key ROUTING_KEY
        channel.basic_publish(exchange = LOGNAME,
                              routing_key = ROUTING_KEY,
                              body = message)
        print ' [x] {} Sent'.format(message)    ##  Print that message
        time.sleep(5)                           ##  Sleep for five seconds
    except KeyboardInterrupt:
        exit()                                  ##  Exeunt
