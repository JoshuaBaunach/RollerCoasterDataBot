#!/usr/bin/python
# This script contains functions that handle the second phase of the RollerCoasterDataBot process.

from lxml import html
import requests
"""
import sys

reload(sys)

sys.setdefaultencoding('utf_8')
"""
# This class defines a roller coaster object and various pieces of info about it
class RollerCoaster:

    # Constructor (takes in basic information about the coaster that all RCDB articles should have.)
    def __init__(self, rcdbid, name, park, locs, status, manufacturer, model1, model2, flag=0):
        self.rcdbid = rcdbid
        self.name = name
        self.park = park
        self.locs = locs
        self.status = status
        self.manufacturer = manufacturer
        self.model1 = model1
        self.model2 = model2
        self.flag = flag

# This class defines a park object
class Park:

    # Constructor
    def __init__(self, rcdbid, name, locs, status, flag=0):
        self.rcdbid = rcdbid
        self.name = name
        self.locs = locs
        self.status = status
        self.flag = flag

class ScraperObject:

    # Constructor
    def __init__(self, query, parkRCDBID=None):
        if (self.isQuery(query)):
            self.query = query
            self.parkRCDBID = parkRCDBID
            response = self.getRCDBID()
            self.rcdbid = response.rcdbid
            self.flag = response.flag
            self.isPark = response.isPark

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
        # Start with the name
        name = unicode(tree.xpath('//div[@class="scroll"]/h1/text()')[0])

        # Branch off: If this is a coaster, extract coaster info, otherwise extract park info
        if (not self.isPark):
            scrollinfo = tree.xpath('//div[@class="scroll"]')
            firstScrollLinks = scrollinfo[0].xpath('a/text()')
            park = unicode(firstScrollLinks[0])
            locs = []
            for location in firstScrollLinks[1:]:
                locs.append(unicode(location))

            # Determine the status of the coaster
            statusArray = tree.xpath('//div[@id="feature"]/a/text()')
            if (len(statusArray) == 0):
                status = "Removed"
            else:
                status = unicode(statusArray[0])
                if (status == "Operated"):
                    status = "Removed"

            if (len(scrollinfo) > 1):
                secondScrollLinks = scrollinfo[1].xpath('a/text()')
                manufacturer = unicode(secondScrollLinks[0])
                if (len(secondScrollLinks) > 1):
                    model1 = unicode(secondScrollLinks[1])
                    model2 = unicode(secondScrollLinks[2])
                else:
                    model1 = None
                    model2 = None
            else:
                manufacturer = unicode('Not Specified')
                model1 = None
                model2 = None

            # Create a coaster object corresponding to the info gathered and return it
            return RollerCoaster(self.rcdbid, name, park, locs, status, manufacturer, model1, model2, self.flag)

        # If the data corresponds to a park
        else:
            scrollinfo = tree.xpath('//div[@class="scroll"]')
            firstScrollLinks = scrollinfo[0].xpath('a/text()')
            locs = []
            for location in firstScrollLinks[1:]:
                locs.append(unicode(location))

            # Determine the status of the park
            statusArray = tree.xpath('//div[@id="feature"]/a/text()')
            if (len(statusArray) == 0):
                status = "Defunct"
            else:
                status = unicode(statusArray[0])
                if (status == "Operated"):
                    status = "Defunct"

            # Create a park object corresponding to the info gathered and return it
            return Park(self.rcdbid, name, locs, status, self.flag)

    # Tries to find an RCDBID that corresponds to the object's query or park name.
    # Input: None
    # Output: An RCDBResponse object containing the response's RCDBID and flag
    def getRCDBID(self):

        # If we're looking through a park, look at that park's RCDB page for the coaster
        if (self.parkRCDBID != None):
            page = requests.get('https://rcdb.com/' + self.parkRCDBID + '.htm')
            pageContent = html.fromstring(page.content)
            coasterRows = pageContent.xpath('//div[@class="scroll nowrap"]/table/tbody/tr')

            # Iterate through each of the coasters, determining if any of them is what we're looking for
            for row in coasterRows:
                rowContent = row.xpath('td/a')

                # Tell whether the first link is a picture or not
                if (len(rowContent[0].values()) != 1):
                    rcdbLink = rowContent[1]
                else:
                    rcdbLink = rowContent[0]

                if (str.lower(rcdbLink.text.encode('utf-8')) == str.lower(self.query.encode('utf-8'))):
                    htmIndex = rcdbLink.values()[0].find('.')
                    return RCDBResponse(rcdbLink.values()[0][1:htmIndex], 0)

            # If all else fails, return no match. :/
            return RCDBResponse(-1, -1)

        # Perform a search on RCDB using this object's query variable
        page = requests.get('https://rcdb.com/qs.htm?qs=' + self.query)
        url = page.url

        # If the url that was returned is not the RCDB suggested results page, return the RCDBID that was found
        if (url.find('qs.htm') == -1):
            # TODO: Determine whether the page is a park
            return RCDBResponse(url[17:-4], 0)

        # If we get to this point, we may have landed on a page of suggested results
        resultsTree = html.fromstring(page.content)
        suggestionPhraseArray = resultsTree.xpath('//div[@id="article"]/div/section/h3/text()')

        # If this is true, then RCDB is suggesting some results
        if (len(suggestionPhraseArray) != 0):
            suggestionPhrase = suggestionPhraseArray[0]
            # Exact match (" Roller Coaster is named "query":)
            if (suggestionPhrase[:24] == ' Roller Coaster is named' or suggestionPhrase[:25] == ' Roller Coaster are named' or suggestionPhrase[:24] == ' Amusement Park is named' or suggestionPhrase[:25] == ' Amusement Park are named'):
                return RCDBResponse(resultsTree.xpath('//div[@id="article"]/div/section/p/a')[0].get('href')[1:-4], 0)

            # Close match (" Roller Coaster name contains the phrase" or " Roller Coaster name starts with")
            if (suggestionPhrase[:40] == ' Roller Coaster name contains the phrase' or suggestionPhrase[:32] == ' Roller Coaster name starts with' or suggestionPhrase[:40] == ' Roller Coaster names contain the phrase' or suggestionPhrase[:32] == ' Roller Coaster names start with'):
                return RCDBResponse(resultsTree.xpath('//div[@id="article"]/div/section/p/a')[0].get('href')[1:-4], 1)
        else:
            suggestionLinkArray = resultsTree.xpath('//div[@id="article"]/div/p/a/text()')

            # If the size of suggestionLinkArray is nonzero, RCDB is suggesting an alternate spelling of the coaster
            if (len(suggestionLinkArray) != 0):
                self.query = suggestionLinkArray[0]
                return RCDBResponse(self.getRCDBID().rcdbid, 2)
            else:
                return RCDBResponse(-1, -1)

# This class will contain the information corresponding to the response of an RCDB query
# Flag Possibilities: -1 = No Match, 0 = Exact Match, 1 = Close Match, 2 = Alternate Spelling
class RCDBResponse:

    def __init__(self, rcdbid, flag):
        self.rcdbid = rcdbid
        self.flag = flag
        if (rcdbid != -1):
            self.isPark = self.determinePark(rcdbid)

        else:
            self.isPark = False

    # This function will return whether a given RCDBID belongs to a park.
    def determinePark(self, rcdbid):
        page = requests.get('https://www.rcdb.com/' + rcdbid + '.htm')

        # Try to find the phrase "Parks Nearby" in the page
        resultsTree = html.fromstring(page.content)
        linkRowArray = resultsTree.xpath('//span[@class="link_row"]/span/a')

        for phrase in linkRowArray:
            if phrase.text == 'Parks nearby':
                return True

        return False
