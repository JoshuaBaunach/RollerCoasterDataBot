#!/usr/bin/python
# This file is the main file that manages everything

from redditManager import RedditManager
import json
import time
import getpass
import sys
import traceback

def main():

    # Clear the logfile
    logfile = open('logfile.log', 'w')
    logfile.write('')
    logfile.close()

    writeLogfile('Starting Program')
    non_api = False
    config_name = 'config.json'

    # Determine if the program is going to run in non-api mode (i.e. read input from console)
    if (len(sys.argv) != 1):
        if ('-n' in sys.argv):
            print 'Running in non-api mode'
            non_api = True
            manager = RedditManager(non_api=False)
        if ('-c' in sys.argv):
            config_name = sys.argv[sys.argv.index('-c')+1]

    if ('-n' not in sys.argv):
        # Read from the config file
        configFile = open(config_name)
        configJSON = json.load(configFile)

        # If no password is provided, prompt for one
        if (configJSON['password'] == ''):
            configJSON['password'] = getpass.getpass('Password for /u/' + configJSON['username'] + ': ')

        # If no user agent is provided, use a default one
        if (configJSON['userAgent'] == ''):
            configJSON['userAgent'] = 'RollerCoasterDataBot: Created by /u/MrManGuy16, being used under /u/RollerCoasterDataBot'

        # Set up the Reddit Manager
        manager = RedditManager(configJSON['clientId'], configJSON['clientSecret'], configJSON['username'], configJSON['password'], configJSON['userAgent'])

    if (not non_api):
        # Check the newest 50 posts for unaccounted queries in each of the whitelisted Subreddits
        try:
            for sub in configJSON['whitelistedSubreddits']:
                manager.findQueries(sub, 50)
        except Exception as excep:
            writeLogfile('Error encountered while searching through comments. Details Below: \n' + excep.message)

        time.sleep(60)

        # Main loop
        while True:

            # Check the newest 10 posts for unaccounted queries in each of the whitelisted Subreddits
            try:
                for sub in configJSON['whitelistedSubreddits']:
                    manager.findQueries(sub, 10)
            except Exception as excep:
                writeLogfile('Error encountered while searching through comments. Details Below: \n' + excep.message)

            time.sleep(60)
    else:

        while True:
            fullText = raw_input('Query to process: ')

            # Try to see if it is a query
            beginIndex = fullText.find('{')

            if (beginIndex != -1):
                endIndex = fullText.find('}', beginIndex)

                if (endIndex != -1):

                    query = fullText[beginIndex+1:endIndex]
                    try:
                        commentText = manager.buildComment(query)
                        print commentText.encode('utf-8')
                    except Exception as excep:
                        commentText = manager.buildErrorComment(excep.message)
                        print commentText.encode('utf-8')
                        print 'Here is what went wrong:'
                        traceback.print_exc()

# Function to write data to the logfile
def writeLogfile(message):
    logfile = open('logfile.log', 'a')

    # Get the timestamp
    timestamp = '[' + time.strftime('%d/%m/%y %H:%M:%S', time.gmtime()) + '] '

    logfile.write(timestamp + message + '\n')

    logfile.close()


if __name__ == '__main__':
    main()
