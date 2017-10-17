#!/usr/bin/python
# The file for managing the bot's interactions with Reddit.

from lxml import html
import rcdbscraper
import prawcore
import praw
# TODO: Remove temporary imports when this file is stable
import getpass
import sys

class RedditManager:

    # Initializer
    def __init__(self, client_id = 'client_id', client_secret = 'client_secret', username = 'username', password = 'password', user_agent = 'RollerCoasterDataBot by /u/MrManGuy16', non_api=False):
        if (not non_api):
            self.redditInstance = praw.Reddit(client_id = client_id, client_secret = client_secret, user_agent = user_agent, username = username, password = password)

    # Function to scan a Subreddit's most recent posts for queries
    # Input: The name of a Subreddit
    # Output: None
    def findQueries(self, targetSubredditName, scanSize):
        targetSubreddit = self.redditInstance.subreddit(targetSubredditName)

        for submission in targetSubreddit.new(limit=scanSize):
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():

                # Try to see if it is a query
                beginIndex = comment.body.find('{')

                if (beginIndex != -1):
                    endIndex = comment.body.find('}', beginIndex)

                    if (endIndex != -1):

                        commentChildren = comment.replies.list()
                        respondedFlag = False
                        for child in commentChildren:
                            if (child.author.name == 'RollerCoasterDataBot'):
                                respondedFlag = True

                        if (not respondedFlag):
                            query = comment.body[beginIndex+1:endIndex]

                            print 'Caught query from /u/' + comment.author.name
                            print 'Query: ' + query
                            try:
                                commentText = self.buildComment(query)
                            except Exception as excep:
                                commentText = self.buildErrorComment(excep.message)

                            comment.reply(commentText)

    # Recursively scans a thread's comment trees for valid queries that have not already been processed.
    # Input: A comment tree
    # Output: None
    # TODO: Look around to see if this function is still used...
    def scanComment(self, comment):
        # Recursively call this function on the children of this comment
        #
        # Try to see if it is a query
        forest = comment.replies
        beginIndex = comment.body.find('{')

        if (beginIndex != -1):
            endIndex = comment.body.find('}', beginIndex)

            if (endIndex != -1):

                # Check to see whether the bot already replied to this query
                respondedFlag = False

                for newComment in forest.list():
                    if newComment.author.name == 'RollerCoasterDataBot':
                        respondedFlag = True

                if (not respondedFlag):
                    query = comment.body[beginIndex+1:endIndex]
                    commentText = self.buildComment(query)
                    comment.reply(commentText)

        # Run the function on all of the comment's children, if any exist
        if (len(forest.list()) == 0):
            return

        for newComment in forest.list():
            self.scanComment(newComment)

    # Builds a comment after an error has been encountered.
    # Input: The error message
    # Output: None
    def buildErrorComment(self, errorMessage):

        finishedComment = ''
        finishedComment += 'Oops, this is embarassing. I encountered an error while processing your query. /u/MrManGuy16 will be notified of the details.'
        finishedComment += '\n\n---\n\n^I am a bot. ^beep boop\n\n^[Creator](/u/MrManGuy16) | [Source](https://www.example.com)'

        finishedComment = finishedComment.replace(' ', '&nbsp;')

        return finishedComment

    # Builds a comment given a user's query
    # Input: String representing a query
    # Output: String representing the formatted comment to be posted
    def buildComment(self, query):

        # Check to see whether the user is including a park to narrow the search
        parkSpecifierIndex = query.find('@')

        finishedComment = ''



        if (parkSpecifierIndex != -1):
            parkScraper = rcdbscraper.ScraperObject(query[parkSpecifierIndex+2:])
            # Determine if the user misspelled the park or it does not exist
            if (parkScraper.rcdbid == -1):
                finishedComment += 'I didn\'t find anything. :\\\n\n'
                scraper_flag = -1
            else:
                scraper = rcdbscraper.ScraperObject(query[:parkSpecifierIndex-1], parkRCDBID = parkScraper.scrapeInformation().rcdbid)
                scraper_flag = scraper.flag
        else:
            scraper = rcdbscraper.ScraperObject(query)
            scraper_flag = scraper.flag

        if (scraper_flag != -1):
            coasterInfo = scraper.scrapeInformation()


        # Check to see whether a result was found in the first place
        if (scraper_flag != -1):
            # If the coaster has a flag, account for it
            if (coasterInfo.flag == 1):
                finishedComment += '^Note: The query did not return an exact match. Using closest result.\n\n'
            elif (coasterInfo.flag == 2):
                finishedComment += '^Note: The query could be misspelled. Using an alternate spelling.\n\n'

            finishedComment += '**' + coasterInfo.name + '** ([RCDB Info](https://www.rcdb.com/' + coasterInfo.rcdbid + '.htm))\n\n'
            finishedComment += coasterInfo.park + ' ('
            for location in coasterInfo.locs:
                finishedComment  += location + ', '

            finishedComment = finishedComment[:-2] + ')\n\n'

            finishedComment += '^Status: ' + coasterInfo.status + ' | Manufacturer: ' + coasterInfo.manufacturer
            if (coasterInfo.model1 != None):
                finishedComment += ' | Model: ' + coasterInfo.model1 + ' / ' + coasterInfo.model2

        else:
            if (scraperFlag != -1):
                finishedComment += 'I didn\'t find anything. :\\\n\n'

        finishedComment += '\n\n---\n\n^I am a bot. ^beep boop\n\n^[Creator](/u/MrManGuy16) | [Source](https://www.example.com)'

        finishedComment = finishedComment.replace(' ', '&nbsp;')

        return finishedComment
