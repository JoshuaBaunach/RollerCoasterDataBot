#!/usr/bin/python
# This script defines a RollerCoaster class that will be used for extracting information.

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


