"""

Author: Sam Celani

File:   V2C_Intercept.py

Description:

    This script listens to wireless communications sent from the vehicle to the
    cloud (mobile lab). It then looks up the approximate road grade and speed limit
    from imported files, and sends them back to the vehicle using send.py.
    
    It is part of the ARPA-E Project: NEXTCAR.


Imported Files:

    configInit.py

        Helps to determine where the script should be listening.


    send.py

        One-off script that sends data back upon being called.


    grad_grid_MTUDC_050318_CD_minaux_Beta_043.mat

        Contains all of the data required to look up the latitude and longitude
        and return a road grade over the MTU Drive Cycle.


    mtudc_speed_limit_grid_mph.mat

        Contains all of the data required to look up the latitude and longitude
        and return a speed limit over the MTU Drive Cycle.
    
"""


###########################################################

#
#   IMPORTS
#       All imports are nested in a try-except block
#       to avoid fatal errors, or at least to simply
#       put them off for a little bit.
#

try:
    
    import configInit                   ##  Used to decide server
    import matplotlib.pyplot as plt     ##  Used in plotting    
    import numpy as np                  ##  Used in plotting
    import pika                         ##  Used in data transmission
    import scipy.io as sp               ##  Used for SL and RG lookup
    import send                         ##  Used to send data
    import sys                          ##  Used for testing
    
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

##  Initialize road grade data
pltLat = []
pltLong = []
rgL = []

##  Open Speed Limit data
bigData = sp.loadmat('mtudc_speed_limit_grid_mph')

##  Pull data from inside the Speed Limit data set
gpsLat = bigData['GPS_Lat']
gpsLong = bigData['GPS_Long']
gpsMPH = bigData['speed_limit_mph']

##  Open Road Grade data
biggerData = sp.loadmat('grad_grid_MTUDC_050318_CD_minaux_Beta_043')

##  Populate Road Grade data for Lookup and Plotting
for b in range(len(biggerData['grade_grid'])):
    for c in range(len(biggerData['grade_grid'][b])):

##  In the matrix, entries are either nan or a valid value
        
        if biggerData['grade_grid'][b][c] > 0 or biggerData['grade_grid'][b][c] < 0:
        ##  Check to see if the value is valid
        
            pltLat.append(biggerData['latitude'][0][b])
            ##  Keep track of valid latitudes
            
            pltLong.append(biggerData['longitude'][0][c])
            ##  Keep track of valid longitudes
            
            rgL.append(biggerData['grade_grid'][b][c])
            ##  Keep track of corresponding road grades


plt.scatter(pltLong, pltLat, marker = '.')      ##  Plot valid lat long pairs
plt.show(block = False)                         ##  Show plot

##  I don't understand this line, but it seems important  -Sam
plt.pause(0.0001)

gpsGradeData = np.array([pltLat, pltLong])      ##  Format Road Grade data for lookup
gpsSpeedData = np.array([gpsLat,gpsLong])       ##  Format Speed Limit data for lookup

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
                                           credentials = CREDENTIALS,
                                           socket_timeout = None)
        
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
                                       credentials = CREDENTIALS,
                                       socket_timeout = None)
    
    print SERVERIP
    print '({0}, {1})'.format(credA, credB)
    print LOGNAME
    print ROUTING_KEY
    print '\n'

##  I don't understand this line, but it seems important  -Sam
plt.ion()

###########################################################

#
#   FUNCTION DEFINITION 1
#       Takes GPS (Lat, Long) and looks up the speed limit
#       at that position
#

def gpsSLLookUp( lat, long ):
    global gpsSpeedData         ##  Collection of valid Speed Limit coordinates
    global gpsMPH               ##  Valid Speed Limits

    ##  Finds the difference between all valid points and the live coordinate
    difSL = [(abs(long - gpsSpeedData[0][c]), abs(lat - gpsSpeedData[1][c])) for c in range(len(gpsSpeedData[0]))]
    ##  Converts difference to distance
    disSL = [ ( ( latDif )**2 + ( longDif )**2 )**0.5 for (latDif, longDif) in difSL ]

    ##  Finds the minimum of the distances
    m = min(disSL)
    ##  Finds index of the minimum distance
    i = disSL.index(m)

    ##  Prints Speed Limit at desired index
    print gpsMPH[i][0]
    ##  Prints corresponding Latitude and Longitude of desired speed limit
    print 'Lat ' + str(gpsSpeedData[0][i])
    print 'Long ' + str(gpsSpeedData[1][i]) + '\n'
    
    return gpsMPH[i][0]     ##  Returns desired speed limit, for use with sending back

###########################################################
    
#
#   FUNCTION DEFINITION 2
#       Takes GPS (Lat, Long) and looks up the road grade
#       at that position
#

def gpsGradeLookUp( lat, long ):
    global gpsGradeData     ##  Collection of valid Road Grade coordinates
    global rgL              ##  Valid Road Grades

    ##  Finds the difference between all valid points and the live coordinate
    dif = [(abs(long - gpsGradeData[0][c]), abs(lat - gpsGradeData[1][c])) for c in range(len(gpsGradeData[0]))]
    ##  Converts difference to distance
    dis = [ ( ( latDif )**2 + ( longDif )**2 )**0.5 for (latDif, longDif) in dif ]

    ##  Finds the minimum of the distances
    m = min(dis)
    ##  Finds index of the minimum distance
    i = dis.index(m)

    ##  Prints Road Grade at desired index
    print rgL[i]
    ##  Prints corresponding Latitude and Longitude of desired road grade
    print 'Lat [' + str(gpsGradeData[0][i]) + ']'
    print 'Long [' + str(gpsGradeData[1][i]) + ']'

    ##  Plots a red X along the drive cycle in the closest point to live GPS coordinates
    plt.scatter(gpsGradeData[1][i],gpsGradeData[0][i],marker = 'x', c = 'red')

    ##  Shows the plot
    plt.show()

    ##  I don't understand this line, but it seems important  -Sam
    plt.pause(0.0001)
    
    return rgL[i]       ##  Returns desired road grade, for use with sending back

###########################################################

#
#   FUNCTION DEFINITION 3
#       Callback, this is what happens when data is received
#           

def callback(ch, method, properties, body):
    global logfile          ##  This is the name of the file that the message gets dumped to
    global SERVERIP         ##  This is the server IP, used for send.fullsend()
    global CREDENTIALS      ##  This is the credentials, used for send.fullsend()
    global LOGNAME          ##  This is the exchange, used for send.fullsend()
    global ROUTING_KEY      ##  This is the routing key, used for send.fullsend()

    
    if len(sys.argv) is 2 and sys.argv[1].lower() == '-v':  ##  V E R B O S E
        print len(body)                                     ##  Prints how long the message was
        print type(body)                                    ##  Prints the type of the message
        
    print ' [x] {}\n'.format(body)           ##  Prints the actual message
    
    with open('V2C_logfile.txt','a') as logfile:    ##  Open the logfile in append mode
        logfile.write(str(body)[44:-1] + '\n')      ##  Writes to logfile, and then closes

    data = str(body).split(', ')        ##  Splits data into usable chunks
       
    sl = gpsSLLookUp( float(data[18]), float(data[17]) )        ##  Send coordinates to search algorithm
    rg = gpsGradeLookUp( float(data[18]), float(data[17]) )     ##  Send coordinates to search algorithm
    
    plt.scatter(float(data[18]), float(data[17]), c = 'green', marker = 'P')  ##  Prints the coordinate 
    plt.show()                                                  ##  Shows the plot

    ##  I don't understand this line, but it seems important  -Sam
    plt.pause(0.0001)                                           

    send.fullSend(sl,
                  rg,
                  serverIP = SERVERIP,
                  creds = CREDENTIALS,
                  xch = LOGNAME,
                  rtk = 'controller_1')       ##  Send data out

        
    print ' [*] Waiting for packets...'

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
                         exchange_type = 'topic',    
                         auto_delete = True)      

##  Declare queue
q = channel.queue_declare(exclusive = True)

##  Bind queue to exchange over routing key
channel.queue_bind(exchange = LOGNAME,
                   queue = q.method.queue,
                   routing_key = ROUTING_KEY)

###########################################################

#
#   TESTING
#

##  Create fake logfile for debugging purposes
if len(sys.argv) is 2 and sys.argv[1].lower() == 'test':
    simStepIndex = 0
    currentTime = 172530.5
    fakePacket1 = "b'1,141.219.181.216,2.5,1.0,1,5,0.1,"
    fakePacket2 = ",10.0,1.5,87,47,True,10.1,1.51,87,47,250,True,10,2560,8,10000,11.0,1.0,0.5,7.7,80'\n"

    with open('V2C_logfileTEST.txt','w') as file:
        for i in range(10):
            simStepIndex += 0.1
            currentTime += 0.1
            file.write(fakePacket1+str(simStepIndex)+','+str(currentTime)+fakePacket2)
    exit()
elif len(sys.argv) is 2 and sys.argv[1].lower() == 'usage':
    print 'python ' + str(sys.argv[0]) + ' test\t\t\t-> Prints sample logfile with fake data and quits.'
    print 'python ' + str(sys.argv[0]) + ' [ANYTHING BUT TEST]\t-> Appends data to file only.'
    print 'python ' + str(sys.argv[0]) + ' \t\t\t-> Appends data to file and prints data to console.'
    exit()


print ' [*] Waiting for packets...'

###########################################################

##  Define consumption
channel.basic_consume(callback,                 ##  Function to be called when receiving data
                      queue = q.method.queue,   ##  Over this queue
                      no_ack = True)            ##  No acknowledgments sent


##  Acutal consumption
try:
                                ##  Consumption is nested in a try-
    channel.start_consuming()   ##  except block, in the hopes that it
except KeyboardInterrupt:       ##  handles a KeyboardInterrupt gracefully. 
                                ##  Spoiler Alert:: It doesn't work very well
    
    exit()                      ##  Exit script
