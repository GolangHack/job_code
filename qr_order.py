#!/usr/bin/env python
# -*- coding: utf-8 -*-
import data_storage.database.connection_manager as manager
import data_storage.database.models_generated as db
from data_storage.database.Card import Card
from calendarEvents import CalendarEvents
from data_storage.database import Program


class QrOrder(object):

    ORDER_DONE = 2
    ORDER_PAID = 4

    def __init__(self, order, calendar):
        self._order = order
        self._calendar = calendar

    def getId(self):
        return self._order.id

    def getStatus(self):
        return self._order.status_id

    def setStatus(self, status):
        self._order.status_id = status
        self._order.save()

    def getClient(self):
        return self._order.client

    def getDate(self):
        return self._order.date

    def getRobotNumber(self):
        return self._order.installation.number

    def setRobotNumber(self, number):
        self._order.installation.number = number
        self._order.save()

    def getProgramNumber(self):
        return self.getPrograms()[0].number

    def getPrograms(self):
        return self._getProgramByType(type=0)

    def getServices(self):
        return self._getProgramByType(type=1)

    def getTotalPrice(self):
        return self._order.sum

    def getOrderPriceDifference(self):
        programs = self.getOrderPrograms()
        p_sum = sum(map(lambda p: self.getCurrentProgramPrice(p), programs))
        services = self.getOrderServices()
        s_sum = sum(map(lambda s: self.getCurrentProgramPrice(s), services))
        return self.getTotalPrice() - (p_sum + s_sum)

    def containsAnyService(self):
        return len(self.getServices()) != 0

    def containsAnyUnavailableService(self):
        services = self.getOrderServices()
        availability = map(lambda s: self._isProgramAllowedNow(s), services)
        return False in availability

    def getCurrentProgramPrice(self, program):
        timeOfDay = self._calendar.getTimeOfDay()
        if timeOfDay == CalendarEvents.DAY:
            return program.dayPrice
        else:
            if program.allowedNight is True:
                return program.nightPrice
            else:
                return program.dayPrice

    def getOrderPrograms(self):
        p_ids = map(lambda p: p.id, self.getPrograms())
        return filter(lambda p: p.id in p_ids, Program.getPrograms())

    def getOrderServices(self):
        s_ids = map(lambda s: s.id, self.getServices())
        return filter(lambda s: s.id in s_ids, Program.getServices())

    def done(self):
        self.setStatus(QrOrder.ORDER_DONE)

    def isPaid(self):
        return self.getStatus() == QrOrder.ORDER_PAID

    def getCard(self):
        client = db.Client.get(db.Client.id == self.getClient())
        account = db.Account.get(db.Account.client == client)
        return db.Card.get(db.Card.account == account)

    def _isProgramAllowedNow(self, program):
        timeOfDay = self._calendar.getTimeOfDay()
        if timeOfDay == CalendarEvents.DAY:
            return program.allowed
        else:
            return program.allowedNight

    @manager.autoConnect
    def _getProgramByType(self, type=0):
        return (db.Program.select()
                .join(db.ClientOrderHasProgram)
                .join(db.ClientOrder)
                .where((self._order.id == db.ClientOrder.id) &
                       (db.Program.program_type == type)))
