"""

Author: Sam Celani

File:   configInit.py

Description:

    This file is imported by many files to correctly determine
    what credentials to wirelessly connect to.
    
    It is part of the ARPA-E Project: NEXTCAR.
    
"""


###########################################################

#
#   IMPORTS
#       All imports are nested in a try-except block
#       to avoid fatal errors, or at least to simply
#       put them off for a little bit.
#

try:

    import sys      ##  Used to see command line arguments

except Exception as ex:
    print ex
    exit()

###########################################################

#
#   GLOBAL VARIABLES
#

config = dict()
ra = []

###########################################################

#
#   FUNCTION DEFINITION 1
#       Initialization function
#

def init(param = None):
    global config
    global ra

    ##  Open file as configFile
    with open('config.txt','r') as configFile:
        for line in configFile:
            ##  If the line isn't an empty line
            if not line == '\n':
                ##  The first part of the file is the field
                field = line.split(',')[0]
                ##  Everything else is part of the data
                data = line.split(',')[1].split('|')
                ##  If there's more than one piece of data
                if len(data) > 1:
                    ##  Add the KVP to the dictionary with the data as a tuple
                    ##  The [:-1] is used to strip the newline from the data
                    config.update( { field : ( data[0], data[1][:-1] ) } )
                ##  If there's only one piece of data
                else:
                    ##  Make a normal dictionary addition
                    config.update( { field : data[0][:-1] } )


    ## Printing info dictionary for debugging
    # for key in config:
    #    print(key,':',config[key])
    
    if param is None:
        
        ##  Print this big ass thing if there's no given argument
        print 'Usage:: [FILENAME].py [PARAM]'
        print 'Param List...\n'
        print 'kuilin\t->\tThis sets the following variables:'
        print '\t\tIP\t\t-> {}'.format(config['kuilin'])
        print '\t\tCred.\t\t-> ( {0}, {1} )'.format( config['credentials'][0], config['credentials'][1] )
        print '\t\tRouting Key\t-> {}'.format(config['routing key_K'])
        print '\t\tExchange\t-> {}\n'.format(config['exchange'])
        
        print 'beta\t->\tThis sets the following variables:'
        print '\t\tIP\t\t-> {}'.format(config['beta'])
        print '\t\tCred.\t\t-> ( {0}, {1} )'.format( config['credentials'][0], config['credentials'][1] )
        print '\t\tRouting Key\t-> {}'.format(config['routing key_B'])
        print '\t\tExchange\t-> {}\n'.format(config['exchange'])

        print 'sam\t->\tThis sets the following variables:'
        print '\t\tIP\t\t-> {}'.format(config['localhost'])
        print '\t\tRouting Key\t-> {}'.format(config['routing key_S'])
        print '\t\tExchange\t-> {}\n'.format(config['exchange'])

        print 'mobile_lab\t->\tThis sets the following variables:'
        print '\t\tIP\t\t-> {}'.format(config['mobile lab'])
        print '\t\tCred.\t\t-> ( {0}, {1} )'.format( config['credentials'][0], config['credentials'][1] )
        print '\t\tRouting Key\t-> {}'.format(config['routing key_M'])
        print '\t\tExchange\t-> {}\n'.format(config['exchange'])

        print 'tony_url\t->\tThis sets the following variables:'
        print '\t\tIP\t\t-> {}'.format(config['tony url'])
        print '\t\tRouting Key\t-> {}'.format(config['routing key_T'])
        print '\t\tExchange\t-> {}\n'.format(config['exchange'])

        print 'override\t->\tThis allows you to input your own information'
        print '\t\t\tConsider editing the file to contain custom information\n\n'

        ##  Prompt the user for input, and gracefully exits in case of a KeyboardInterrupt
        try:
            usr = input('Press CTRL + C to exit\n').lower().split(' ')      ##  .lower().split(' ') converts the input to lower case and splits it over the spaces
        except KeyboardInterrupt:
            exit()

        
        if len(usr) >= 1:       ##  If the length of the list is one or more
            init(usr[0])        ##  Take the first position, or the only position if the length is one
            exit()
        else:
            init()              ##  Otherwise, print the above crap and try again


    elif param.lower() == 'kuilin':         ##  If the user inputs kuilin
        ra = [config['kuilin'],config['credentials'],config['exchange'],config['routing key_K']]        ##  Necessary data that corresponds to kuilin
    elif param.lower() == 'beta':           ##  If the user inputs beta
        ra = [config['beta'],config['credentials'],config['exchange'],config['routing key_B']]          ##  Necessary data that corresponds to beta
    elif param.lower() == 'sam':            ##  If the user inputs sam
        ra = [config['localhost'],(None, None),config['exchange'],config['routing key_S']]              ##  Necessary data that corresponds to sam
    elif param.lower() == 'mobile_lab':     ##  If the user inputs mobile_lab
        ra = [config['mobile lab'],config['credentials'],config['exchange'],config['routing key_M']]    ##  Necessary data that corresponds to mobile_lab
    elif param.lower() == 'tony_url':       ##  If the user inputs tony_url
        ra = [config['tony url'],config['exchange'],config['routing key_T']]                            ##  Necessary data that corresponds to tony_url
    elif param.lower() == 'override' or param.lower() == 'ov':              ##  Override mode

        ##  Begin override mode
        print 'Press ENTER to skip any of the following fields.\n'
        
        ip = input('What IP are you connecting to?\t')
        ##  if ip has 0 characters (is just an ENTER), append None
        if not len(ip) is 0:
            ra.append(ip)
        else:
            ra.append(None)
            
        usr = input('Username?\t\t\t')
        pas = input('Password?\t\t\t')
        ##  if either usr or pas has 0 characters (is just an ENTER), append (None, None)
        if len(usr) is 0 or len(pas) is 0:
            ra.append( ( None, None ) )
        else:
            ra.append( ( usr, pas ) )
            
        xch = input('Through what exchange?\t\t')
        ##  if xch has 0 characters (is just an ENTER), append None
        if not len(xch) is 0:
            ra.append(xch)
        else:
            ra.append(None)
            
        rtk = input('With what routing key?\t\t')
        ##  if rtk has 0 characters (is just an ENTER), append None
        if not len(rtk) is 0:
            ra.append(rtk)
        else:
            ra.append(None)

        print '\n'

    else:
        init()

    return ra
        


#### Testing
##if len(sys.argv) > 1:
##    init(str(sys.argv[1]))
##else:
##    init()


