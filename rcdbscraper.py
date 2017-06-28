#!/usr/bin/python
# This script contains functions that handle the second phase of the RollerCoasterDataBot process.

from rollercoaster import RollerCoaster
from lxml import html
import requests

class ScraperObject:

    # Constructor
    def __init__(self, query):
        if (self.isQuery(query)):
            self.query = query
        else:
            # TODO: Replace with capability to PM user of exception
            raise Exception("Not a valid query")

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
    # Input: String corresponding to the coaster's RCDB ID.
    # Output: RollerCoaster object corresponding to the information gathered about the particular coaster.
    def scrapeInformation(self, rcdbid):

        # Create an object from the page and extract its content
        page = requests.get('https://rcdb.com/' + rcdbid + '.htm')
        tree = html.fromstring(page.content)

        # Extract the information we are interested in
        name = tree.xpath('//div[@class="scroll"]/h1/text()')[0]

        scrollinfo = tree.xpath('//div[@class="scroll"]/a/text()')
        park = scrollinfo[0]
        loc1 = scrollinfo[1]
        loc2 = scrollinfo[2]
        loc3 = scrollinfo[3]

        status = tree.xpath('//div[@id="feature"]/a/text()')[0]

        manufacturer = scrollinfo[4]
        model1 = scrollinfo[5]
        model2 = scrollinfo[6]

        # Create a coaster object corresponding to the info gathered and return it
        return RollerCoaster(rcdbid, name, park, loc1, loc2, loc3, status, manufacturer, model1, model2)

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

testObj = ScraperObject("Lightning Rod")
print testObj.getRCDBID()
