#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from calendarEvents import CalendarEvents

log = logging.getLogger(__name__)

class Utility(object):
    def __init__(self, \
                 group,
                 index,  \
                 caption, \
                 price_day, \
                 price_night, \
                 enabled, \
                 calendar, \
                 hasOptions=True):
        self.index = index
        self.group = group
        self.caption = caption
        self.price_day = price_day
        self.price_night = price_night
        self.enabled = enabled
        self.calendar = calendar
        self._hasOptions = hasOptions

    def getIndex(self):
        return self.index

    def getCaption(self):
        return self.caption

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def isEnabled(self):
        return self.enabled and not self.group.isDisabledAtNight()

    def getPrice(self):
        timeOfDay = self.calendar.getTimeOfDay()
        return self.price_day if timeOfDay == CalendarEvents.DAY else self.price_night

    def getNightPrice(self):
        return self.price_night

    def hasOptions(self):
        return self._hasOptions

class UtilityGroup(object):
    def __init__(self, name, calendar, priceCalendar, disabledAtNight):
        self.calendar = calendar
        self.priceCalendar = priceCalendar
        self.disabledAtNight = disabledAtNight
        self.name = name
        self.utilities = []

    def isDisabledAtNight(self):
        timeOfDay = self.calendar.getTimeOfDay()
        return self.disabledAtNight and timeOfDay == CalendarEvents.NIGHT

    def addUtility(self, index, caption, price_day, price_night, enabled, hasOptions=True):
        u = Utility(self, index, caption, price_day, price_night, enabled, self.priceCalendar,
                    hasOptions)
        self.utilities.insert(index, u)
        return u

    def getByIndex(self, index):
        return self.utilities[index]

    def asList(self):
        return self.utilities

class UtilityManager(object):
    def __init__(self, calendar, priceCalendar):
        self.groups = {}
        self.calendar = calendar
        self.priceCalendar = priceCalendar

    def registerUtility(self, \
                        groupName, \
                        index, \
                        caption, \
                        price_day, \
                        price_night, \
                        enabled, \
                        nightDisabled, \
                        hasOptions=True):
        if (groupName not in self.groups):
            log.info('Added new utility group: %s', groupName)
            self.groups[groupName] = UtilityGroup(groupName, self.calendar, self.priceCalendar,
                                                  nightDisabled)
        u = self.groups[groupName].addUtility(index, caption, price_day, price_night, enabled,
                                              hasOptions)
        log.info('Registered new utility class %s, index %s', groupName, index)
        return u

    def isDisabledAtNight(self, groupName):
        return self.groups[groupName].isDisabledAtNight()

    def getUtilities(self, groupName):
        return self.groups[groupName].asList()

    def getUtility(self, groupName, index):
        return self.groups[groupName].getByIndex(index)


