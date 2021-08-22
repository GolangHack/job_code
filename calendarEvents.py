#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging #импортируем библиотеку
import time

from apscheduler.jobstores.base import JobLookupError
from astral import Astral
from apscheduler.schedulers.background import BackgroundScheduler

'https://github.com/agronholm/apscheduler'
import datetime

class CalendarEvents(object):
    SUMMER = 'summer'
    WINTER = 'winter'
    DAY = 'day'
    NIGHT = 'night'

    def __init__(self, \
                 summerStartMonth, \
                 summerEndMonth, \
                 dayStart = 9,\
                 nightStart = 21,\
                 dayNightBySunset = False):

        self._log = logging.getLogger(__name__)
        self.summerStartMonth = summerStartMonth
        self.summerEndMonth = summerEndMonth
        self._dayNightBySunset = dayNightBySunset
        self._dayStart = dayStart
        self._nightStart = nightStart
        self._changeTimeOfDayHandler = None

        self.season = None
        self.day = None
        self.sched = BackgroundScheduler()
        self.sched.start()

        'Job variables'
        self.summerStartJob = None
        self.summerEndJob = None
        self.sunsetJob = None
        self.sunriseJob = None
        self.sunriseHour = None
        self.sunsetHour = None

        'Readjust Cron jobs'
        self.summerStartJob = self.sched.add_job(self.setSummer, 'cron', \
                                                 month=str(self.summerStartMonth),\
                                                 misfire_grace_time=3200)
        self.summerEndJob = self.sched.add_job(self.setWinter,'cron', \
                                                month=str(self.summerEndMonth),\
                                                misfire_grace_time=3200)
        self.setChangeSunsetSunriseJob()
        self.updateActualData()

    def updateActualData(self):
        """Вызвать все функции зависимые от текущей даты"""
        self.setActualSeason()
        self.setActualTimeOfDay()

    def registerChangeTimeOfDayHandler(self, handler):
        self._changeTimeOfDayHandler = handler


    def getTimeOfDay(self):
        return self.timeOfDay

    def getSeason(self):
        return self.season

    def setActualTimeOfDay(self):
        currentDT = datetime.datetime.now()
        hour = currentDT.hour
        self._log.info("Current hour: {}".format(hour))

        if self.sunsetHour < self.sunriseHour:
            'sunset is next day. for example night start at 1am and end at 7am'
            if hour >= self.sunsetHour and hour < self.sunriseHour:
                self.setNight()
            else:
                self.setDay()
        else:
            if hour >= self.sunriseHour and hour < self.sunsetHour:
                self.setDay()
            else:
                self.setNight()

    def setActualSeason(self):
        currentDT = datetime.datetime.now()
        month = currentDT.month
        self._log.info("Current month: {}".format(month))

        if month > self.summerStartMonth and month < self.summerEndMonth:
            self.setSummer()
        else:
            self.setWinter()

    def setChangeSunsetSunriseJob(self):
        currentDT = datetime.datetime.now()
        year = currentDT.year
        month = currentDT.month
        day = currentDT.day
        hour = currentDT.hour

        city_name = 'Vilnius'
        a = Astral()
        a.solar_depression = 'civil'
        city = a[city_name]

        if self._dayNightBySunset:
            sun = city.sun(date=datetime.date(year, month, day))
            self.sunriseHour = sun['sunrise'].hour
            self.sunsetHour = sun['sunset'].hour
        else:
            self.sunriseHour = self._dayStart
            self.sunsetHour = self._nightStart

        'Readjust Sunset and Sunrise'
        try:
            if self.sunsetJob is not None:
                self.sunsetJob.remove()
            if self.sunriseJob is not None:
                self.sunriseJob.remove()
            self.sunsetJob = self.sched.add_job(self.setNight, 'cron', hour=str(self.sunsetHour),\
                                                     misfire_grace_time=3200)
            self.sunriseJob = self.sched.add_job(self.setDay, 'cron', hour=str(self.sunriseHour),\
                                                     misfire_grace_time=3200)
            self._log.info('Sunrise time readjusted. Next sunrise: %s', self.sunriseHour)
            self._log.info('Sunset time readjusted. Next sunset: %s', self.sunsetHour)
        except JobLookupError as e:
            self._log.error('JobLookupError(no switch day-night process): %s', e.message)

    def setSummer(self):
        self.season = self.SUMMER
        self._log.info('Season changed to %s', self.season)

    def setWinter(self):
        self.season = self.WINTER
        self._log.info('Season changed to %s', self.season)

    def setDay(self):
        self.timeOfDay = self.DAY
        self._log.info('Time of day changed to %s', self.timeOfDay)
        self.setChangeSunsetSunriseJob()
        if self._changeTimeOfDayHandler is not None:
            self._changeTimeOfDayHandler(self.timeOfDay)

    def setNight(self):
        self.timeOfDay = self.NIGHT
        self._log.info('Time of day changed to %s', self.timeOfDay)
        self.setChangeSunsetSunriseJob()
        if self._changeTimeOfDayHandler is not None:
            self._changeTimeOfDayHandler(self.timeOfDay)

    def setMinTest(self):
        print "Test cron job: ", self.testCounter
        self.testCounter += 1
        if self.testCounter >3:
            if self.testJob is not None:
                self.testJob.remove()
                self.testJob = None

    def changeTime(self, season, timeOfDay):
        'Time of day'
        if timeOfDay == self.DAY:
            self.setDay()
        elif timeOfDay == self.NIGHT:
            self.setNight()
        self._log.info('Time of day changed to %s', timeOfDay)
        'Season'
        if season == self.SUMMER:
            self.setSummer()
        elif season == self.WINTER:
            self.setWinter()
        self._log.info('Season changed to %s', season)

def test():
    import random
    tiny = "".join([chr(random.randint(0, 255)) for x in range(30)])
    time.sleep(10)

if __name__ == "__main__":
    import logging
    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    scheduler = BackgroundScheduler()
    scheduler.add_job(test, 'interval', seconds=1, misfire_grace_time=1)
    scheduler.start()
    try:
        while True:
            time.sleep(65)
            print("tick")
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
