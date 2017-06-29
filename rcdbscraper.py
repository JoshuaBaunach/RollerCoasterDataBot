#!/usr/bin/python
# This script contains functions that handle the second phase of the RollerCoasterDataBot process.

from lxml import html
import requests

# This class defines a roller coaster object and various pieces of info about it
class RollerCoaster:

    # Constructor (takes in basic information about the coaster that all RCDB articles should have.)
    def __init__(self, rcdbid, name, park, loc1, loc2, loc3, status, manufacturer, model1, model2):
        self.rcdbid = rcdbid
        self.name = name
        self.park = park
        self.loc1 = loc1
        self.loc2 = loc2
        self.loc3 = loc3
        self.status = status
        self.manufacturer = manufacturer
        self.model1 = model1
        self.model2 = model2

class ScraperObject:

    # Constructor
    def __init__(self, query):
        if (not self.isQuery(query)):
            raise Exception("Not a valid query")

        self.query = query
        self.rcdbid = self.getRCDBID()

        if (self.rcdbid == -1):
            raise Exception("Query not found on RCDB")

    # Validates that a given string can be a query
    # TODO: Determine what constitutes a valid query
    # Input: String that could be a query
    # Output: Boolean corresponding to whether it is a valid query
    def isQuery(self, possibleQuery):
        if (possibleQuery == ""):
            return False
        else:
            return True

    # Returns some basic information about a roller coaster given its RCDB ID.
    # Input: None
    # Output: RollerCoaster object corresponding to the information gathered about the particular coaster.
    def scrapeInformation(self):

        # Create an object from the page and extract its content
        page = requests.get('https://rcdb.com/' + self.rcdbid + '.htm')
        tree = html.fromstring(page.content)

        # Extract the information we are interested in
        name = tree.xpath('//div[@class="scroll"]/h1/text()')[0]

        scrollinfo = tree.xpath('//div[@class="scroll"]/a/text()')
        park = scrollinfo[0]
        loc1 = scrollinfo[1]
        loc2 = scrollinfo[2]
        loc3 = scrollinfo[3]

        # Determine the status of the coaster
        statusArray = tree.xpath('//div[@id="feature"]/a/text()')
        if (len(statusArray) == 0):
            status = "Removed"
        else:
            status = statusArray[0]
            if (status == "Operating"):
                status = "Currently Operating"
            elif (status == "Operated"):
                status = "Removed"

        manufacturer = scrollinfo[4]

        if (len(scrollinfo) > 5):
            model1 = scrollinfo[5]
            model2 = scrollinfo[6]
        else:
            model1 = None
            model2 = None

        # Create a coaster object corresponding to the info gathered and return it
        return RollerCoaster(self.rcdbid, name, park, loc1, loc2, loc3, status, manufacturer, model1, model2)

    # Tries to find an RCDBID that corresponds to the object's query.
    # Input: None
    # Output: String corresponding to the coaster's RCDBID (will be '0' if no match was found)
    def getRCDBID(self):

        # Perform a search on RCDB using this object's query variable
        page = requests.get('https://rcdb.com/qs.htm?qs=' + self.query)
        url = page.url

        # If the url that was returned is not the RCDB suggested results page, return the RCDBID that was found
        if (url.find('qs.htm') == -1):
            return url[17:-4]

        # If we get to this point, we may have landed on a page of suggested results
        resultsTree = html.fromstring(page.content)
        suggestionPhraseArray = resultsTree.xpath('//div[@id="article"]/div/section/h3/text()')

        # If this is true, then RCDB is suggesting some results
        if (len(suggestionPhraseArray) != 0):
            suggestionPhrase = suggestionPhraseArray[0]
            # Exact match (" Roller Coaster is named "query":)
            if (suggestionPhrase[:24] == ' Roller Coaster is named' or suggestionPhrase[:25] == ' Roller Coaster are named'):
                return resultsTree.xpath('//div[@id="article"]/div/section/p/a')[0].get('href')[1:-4]

            # Close match (" Roller Coaster name contains the phrase" or " Roller Coaster name starts with")
            if (suggestionPhrase[:40] == ' Roller Coaster name contains the phrase' or suggestionPhrase[:32] == ' Roller Coaster name starts with' or suggestionPhrase[:40] == ' Roller Coaster names contain the phrase' or suggestionPhrase[:32] == ' Roller Coaster names start with'):
                # TODO: Set up a flag for when a close match was found
                return resultsTree.xpath('//div[@id="article"]/div/section/p/a')[0].get('href')[1:-4]
        else:
            suggestionLinkArray = resultsTree.xpath('//div[@id="article"]/div/p/a/text()')

            # If the size of suggestionLinkArray is nonzero, RCDB is suggesting an alternate spelling of the coaster
            if (len(suggestionLinkArray) != 0):
                self.query = suggestionLinkArray[0]
                return self.getRCDBID()
            else:
                return -1


testObj = ScraperObject("Diamondback")

if (testObj.rcdbid != -1):
    coaster = testObj.scrapeInformation()
    print coaster.rcdbid
    print coaster.name
    print coaster.park
    print coaster.status
    print coaster.manufacturer
    print coaster.model1
    print coaster.model2
