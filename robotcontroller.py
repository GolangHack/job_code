#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from pyutils.stopablethread import StopableThread
from pyutils.delay import Delay
import logging, time
from calendarEvents import CalendarEvents
from collections import deque
import pickle
import glob, os
from data_storage.database import models_generated as db
from data_storage.database import connection_manager as cm


class DatabaseQueue(object):
    @cm.autoConnect
    def __init__(self, robotNumber):
        "Загрузить из бд все что есть"
        self.lastCar = None
        self.robotNumber = robotNumber

    @cm.autoConnect
    def addCar(self, queueNumber, program, services, zone="green", attribute=0):
        self.lastCar = db.QueueOnRobots.create(
            robot_number=self.robotNumber, queue_number=queueNumber,
            washing_program=program.number, zone=zone, attribute=attribute)
        db.QueueOnRobotsHasProgram.create(queue_on_robots=self.lastCar.id,
                                          program=program.id)
        for service in services:
            db.QueueOnRobotsHasProgram.create(queue_on_robots=self.lastCar.id,
                                              program=service.id)

    @cm.autoConnect
    def getGreenZoneLength(self):
        return (db.QueueOnRobots.select()
                .where((db.QueueOnRobots.robot_number == self.robotNumber) &
                       (db.QueueOnRobots.zone == "green"))).count()

    @cm.autoConnect
    def getYellowZoneLength(self):
        return (db.QueueOnRobots.select()
                .where((db.QueueOnRobots.robot_number == self.robotNumber) &
                       (db.QueueOnRobots.zone == "yellow"))).count()

    @cm.autoConnect
    def finishWashing(self):
        if self.getYellowZoneLength() > 0:
            # Delete leaving cars from QueueOnRobotsHasProgram
            leaving_cars = (db.QueueOnRobots.select()
                            .where((db.QueueOnRobots.robot_number == self.robotNumber) &
                                   (db.QueueOnRobots.zone == 'red')))
            for car in leaving_cars:
                query = (db.QueueOnRobotsHasProgram.delete()
                         .where(db.QueueOnRobotsHasProgram.queue_on_robots == car.id))
                query.execute()
            # Delete leaving cars from QueueOnRobots
            query = (db.QueueOnRobots.delete()
                     .where((db.QueueOnRobots.robot_number == self.robotNumber) &
                            (db.QueueOnRobots.zone == 'red')))
            query.execute()
        # Move car from yellow to red zone
        query = (db.QueueOnRobots.update({db.QueueOnRobots.zone: "red"})
                 .where((db.QueueOnRobots.robot_number == self.robotNumber) &
                        (db.QueueOnRobots.zone == "yellow")))
        query.execute()

    @cm.autoConnect
    def popGreen(self):
        """
        Сдвигает очередь.
        :return: (номер чека, номер программы)
        """
        logging.getLogger(__name__).info('RobotController on robot {} '
                                         'call popGreen()'.format(self.robotNumber + 1))
        q = (db.QueueOnRobots
             .update({db.QueueOnRobots.zone: "yellow"})
             .where((db.QueueOnRobots.robot_number == self.robotNumber) &
                    (db.QueueOnRobots.zone == "green"))
             .order_by(db.QueueOnRobots.id)
             .limit(1))
        q.execute()

        carToWash = db.QueueOnRobots.get((db.QueueOnRobots.robot_number == self.robotNumber) &
                                         (db.QueueOnRobots.zone == "yellow"))
        return carToWash.queue_number, carToWash.washing_program, carToWash.attribute

    @cm.autoConnect
    def setFinance(self, finance):
        logging.getLogger(__name__).info("Set finance ID to last car")
        q = (db.QueueOnRobots
             .update({db.QueueOnRobots.finance_id: finance})
             .where(db.QueueOnRobots.id == self.lastCar.id))
        q.execute()

    @cm.autoConnect
    def getLastQueueNumber(self):
        if (db.QueueOnRobots
                .select()
                .where(db.QueueOnRobots.robot_number == self.robotNumber)
                .count()) > 0:
            lastClient = (db.QueueOnRobots
                            .select()
                            .where(db.QueueOnRobots.robot_number == self.robotNumber)
                            .order_by(db.QueueOnRobots.id.desc()))
            return lastClient[0].queue_number
        else:
            return 1

    @cm.autoConnect
    def getNextQueueNumber(self):
        record = (db.QueueOnRobots
                    .select()
                    .where((db.QueueOnRobots.robot_number == self.robotNumber) &
                           (db.QueueOnRobots.zone == 'green'))
                    .order_by(db.QueueOnRobots.id)
                    .limit(1)
                    .first())
        return record.queue_number if record else None


class RobotController(StopableThread):

    ROBOT_POLLING_PERIOD = 1.0
    MODE_SYNC_GET = 0
    MODE_SYNC_SET = 1

    def __init__(self,
                 robotNumber,
                 calendar,
                 modbusSerialProvider,
                 entryGate,
                 orderDisplay,
                 leisuWash,
                 entryGateClosingDelay,
                 open_side_gate_with_exit_gate,
                 description='Robot controller ',
                 queue_limit=0,
                 inviteDelay=10,
                 exitGate=None,
                 closeEntryGateOnCarEnter=True,
                 smart_queue_enabled=False,
                 signals={}):
        StopableThread.__init__(self, name='Robot')
        self.description = description
        self.carsQueue = DatabaseQueue(robotNumber)
        self.leisuWash = leisuWash
        self.entryGate = entryGate
        self.exitGate = exitGate
        self._closeEntryGateOnCarEnter = closeEntryGateOnCarEnter
        self._smart_queue_enabled = smart_queue_enabled
        self.orderDisplay = orderDisplay
        self.modbusSerialProvider = modbusSerialProvider
        self.calendar = calendar
        self.queueNumber = self.carsQueue.getLastQueueNumber()
        self.robotWorking = False
        self.program = 0
        self._robotNumber = robotNumber + 1
        self._syncProgramCountDb = None
        self._onErrorArgs = []
        self._onErrorKwargs = {}
        self._onErrorHandler = None
        self._good = False
        self._error_trig = False
        self._acc_trig = False
        self._err = False
        self._acc = False
        self._carInvited = False
        self._gatesDaytimeOpened = False
        self._washing = False
        self._currentQueue = 0
        self._inviteDelay = inviteDelay
        self.queue_limit = queue_limit
        self._programs = {}
        self._manualUsageCount = 0
        self._washesCount = 0
        self._washesOffset = 0
        self._lastUpdate = ''
        self._log = logging.getLogger(__name__)
        self._attribute = 0
        self.entryGateClosingDelay = entryGateClosingDelay
        self.gateReadyToClose = None
        self.open_side_gate_with_exit_gate = open_side_gate_with_exit_gate
        self._isNextQueueNumberDisplayed = False
        self.sig_RobotConnectionLost = signals[
            'Robot#{}.ConnectionLost'.format(self._robotNumber)]
        self.sig_RobotError = signals[
            'Robot#{}.Error'.format(self._robotNumber)]
        self.sig_RobotManualStart = signals[
            'Robot#{}.ManualStart'.format(self._robotNumber)]
        self.start(delay=0)

    def registerProgramCountDbHandler(self, handler):
        self._syncProgramCountDb = handler
        self._syncProgramCountDb(self, mode=RobotController.MODE_SYNC_GET)

    def getRobotNumber(self):
        return self._robotNumber

    def getProgramStatistics(self):
        return [self._programs, self._lastUpdate,
                self._manualUsageCount, self._washesCount,
                self._washesOffset]

    def entry(self, *args, **kwargs):
        self.orderDisplay.displayFree()

    def setGateReadyToClose(self, isReady):
        self.gateReadyToClose = isReady

    def worker(self, timedout, command, **kwargs):
        self._acc, self._err = self._checkGood()
        if self._acc and not self._err:
            if self.sig_RobotError.isActive:
                self.sig_RobotError.deactivate()
            if self.sig_RobotConnectionLost.isActive:
                self.sig_RobotConnectionLost.deactivate()
            if self.robotWorking:
                ' now we are working'
                if not self.leisuWash.isWashing():
                    ' washing process was finished and car leave '
                    self.robotWorking = False
                    self._washing = False
                    self._log.info(self.description + "Washing now end")
                    if self.open_side_gate_with_exit_gate:
                        self.openExitGate(openSideGate=True)
                    else:
                        self.openExitGate(openSideGate=self._attribute == 1)
                elif not self._washing:
                    if self.leisuWash.isCarInPosition() and self.gateReadyToClose is True:
                        self._log.info(self.description + "Car in Position, washing begins")
                        self._washing = True
                        self.orderDisplay.displayBusy()
                        if self._smart_queue_enabled:
                            self.showNextQueueNumberOnDisplayIfExist()
                        if self.isEntryGateShouldBeClosed():
                            self.closeEntryGate()
                        self.setGateReadyToClose(False)
            else:
                self._washing = False
                if self.leisuWash.isStartPossible():
                    time.sleep(self._inviteDelay)
                    self.carsQueue.finishWashing()
                    self.inviteCar()
                elif self._error_trig is True or self._acc_trig is True:
                    self.orderDisplay.displayFree()
                    if self._smart_queue_enabled:
                        self._isNextQueueNumberDisplayed = False
                self._error_trig = False
                self._acc_trig = False
        elif self._acc and self._err and not self._error_trig:
            ' connection to robot is fine but robot in error state'
            self._error_trig = True
            self.sig_RobotError.activate()
            if self.robotWorking:
                if self._onErrorHandler is not None:
                    self._onErrorHandler(self.description + " в ошибочном состоянии", *self._onErrorArgs, **self._onErrorKwargs)
                self._log.warning(self.description + " in error state")
                self.openEntryGate()
                self.robotWorking = False
            self.orderDisplay.displayProhibition()
        elif not self._acc and not self._acc_trig:
            ' connection to robot is lost '
            self._acc_trig = True
            self.sig_RobotConnectionLost.activate()
            if self.robotWorking:
                if self._onErrorHandler is not None:
                    self._onErrorHandler(self.description + " потеряна связь", *self._onErrorArgs, **self._onErrorKwargs)
                self._log.warning(self.description + " connection lost")
            self.orderDisplay.displayProhibition()

        return self.ROBOT_POLLING_PERIOD

    def _checkGood(self):
        acc = False
        self._err = False
        if self.leisuWash.isWasherAccessible():
            acc = True
            if self.leisuWash.inErrorState():
                self._err = True
        self._acc = acc
        self._good = self._acc and not self._err
        return self._acc, self._err

    def isGood(self):
        return self._good

    def getCarsInQueue(self):
        return self.carsQueue.getGreenZoneLength()

    def isRobotOccupied(self):
        return self.carsQueue.getGreenZoneLength() > self.queue_limit - 1

    def registerOnErrorHandler(self, handler, *args, **kwargs):
        self._onErrorArgs = args
        self._onErrorKwargs = kwargs
        self._onErrorHandler = handler

    def startRobot(self, washingProgram):
        self.robotWorking = True
        if washingProgram == 0:
            self.leisuWash.startStandard()
        elif washingProgram == 1:
            self.leisuWash.startFine()
        elif washingProgram == 2:
            self.leisuWash.startPremium()
        elif washingProgram == 3:
            self.leisuWash.startEconom()
        self.updateProgramCount(washingProgram)
        self._log.info(self.description + ' Robot started %s program', washingProgram)

    def requestToEnter(self, program, services, attribute=0, *args, **kwargs):
        if self.queueNumber < 99:
            self.queueNumber += 1
        else:
            self.queueNumber = 1
        self.carsQueue.addCar(queueNumber=self.queueNumber, program=program,
                              services=services, attribute=attribute)
        self._log.info(self.description + 'Received request to enter. '
                                          'Turn number: %s. '
                                          'Program name: %s. '
                                          'Attribute: %s', self.queueNumber, program.name, attribute)
        if self._smart_queue_enabled and self._washing and not self._isNextQueueNumberDisplayed:
            self.showNextQueueNumberOnDisplayIfExist()
        return self.queueNumber

    def showNextQueueNumberOnDisplayIfExist(self):
        next_queue_number = self.carsQueue.getNextQueueNumber()
        if next_queue_number is None:
            self._log.info(self.description +
                           'Next queue number is none, nothing to show')
            self._isNextQueueNumberDisplayed = False
        else:
            self._log.info(self.description +
                           'Show next queue number on display: ' +
                           str(next_queue_number))
            self.orderDisplay.displayNext(next_queue_number)
            self._isNextQueueNumberDisplayed = True

    def inviteCar(self):
        car_waiting = (self.carsQueue.getGreenZoneLength() != 0)
        if car_waiting:
            queueNumber, washingProgram, self._attribute = self.carsQueue.popGreen()
            self._log.info('Invite next car on robot {} (num in queue: {} program: {}). '
                           'Cars in order: {}'.format(self._robotNumber,
                                                      queueNumber,
                                                      washingProgram,
                                                      car_waiting))
            if (queueNumber is not None) and (washingProgram is not None):
                self._log.info(self.description +
                               'Car {} invited to enter to wash by {} program'
                               .format(queueNumber, washingProgram))
                self.orderDisplay.displayInvitation(queueNumber)
                self._currentQueue = queueNumber
                self.openEntryGate()
                Delay.once(self.entryGateClosingDelay, self.setGateReadyToClose, True)
                self.startRobot(washingProgram)
            else:
                self._log.error(self.description + 'turn error!')
        else:
            self.orderDisplay.displayFree()

    def setGatesDaytimeOpened(self, opened):
        self._gatesDaytimeOpened = opened

    def openEntryGate(self, *args, **kwargs):
        # if not self.gates.isGatesOpened():
        self.entryGate.openGates(*args, **kwargs)
        # else:
        #     logging.info("Gates already opened")

    def openExitGate(self, *args, **kwargs):
        if self.exitGate is not None:
            self.exitGate.openGates(*args, **kwargs)

    def closeExitGate(self, *args, **kwargs):
        if self.exitGate is not None:
            self.exitGate.closeGates(*args, **kwargs)

    def isEntryGateShouldBeClosed(self):
        timeOfDay = self.calendar.getTimeOfDay()
        season = self.calendar.getSeason()
        return (season == CalendarEvents.WINTER or \
                timeOfDay == CalendarEvents.NIGHT or \
                not self._gatesDaytimeOpened) and self._closeEntryGateOnCarEnter

    def closeEntryGate(self, *args, **kwargs):
        # if self.gates.isGatesOpened():
        self.entryGate.closeGates(*args, **kwargs)
        # else:
        #     logging.info("Gates already closed")

    def setFinance(self, finance):
        """Добавляет financeID к очереди (выбранные проги, сервисы)"""
        self.carsQueue.setFinance(finance)

    def updateProgramCount(self, program):
        self._programs[program] += 1
        self.checkManualUsage()
        self._washesCount += 1
        self._syncProgramCountDb(self, RobotController.MODE_SYNC_SET)

    def updateProgramStatistics(self, robot):
        counters, numbers = robot.getProgramCounters()
        for k in range(len(numbers)):
            self._programs[numbers[k]] = counters[k]
        self._lastUpdate = robot.getLastTimeUpdate('ProgramCount')
        if self._lastUpdate in ('', 'beginning of a shift'):
            self._lastUpdate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self._manualUsageCount = robot.getManualUsageCounter()
        self._washesCount = robot.getWashesCount()
        self._washesOffset = robot.getWashesOffset()

    def getTotalWashes(self):
        total = 0
        for k in self._programs.keys():
            total += self._programs[k]
        return total

    def checkManualUsage(self):
        washesFromRobot = self.leisuWash.getWashesTotalNumber()
        if washesFromRobot is not None:
            washesDiff = washesFromRobot - self._washesCount
            if washesDiff == 0:
                self._log.info(
                    self.description + 'Washes count equals with database.')
            elif washesDiff > 0:
                now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                self._log.warning(
                    self.description +
                    'Manual usages are registered: from {} to {}, {} times.'
                    .format(self._lastUpdate, now, str(washesDiff)))
                self._washesCount = washesFromRobot
                self._manualUsageCount += washesDiff
                self.sig_RobotManualStart.activate(
                    details=(u'Зарегистрированы ручные запуски: с {} по {}, '
                             u'{} раз(а).'
                             .format(self._lastUpdate, now, str(washesDiff))))
            elif washesDiff in range(-10, 0):
                self._log.warning(
                    self.description +
                    'Washes count is < {} than in database. '
                    'Decrement washes counter in database.'.format(washesDiff))
                self._washesCount += washesDiff
            else:
                self._log.warning(
                    self.description +
                    'Washes count reset are registered: '
                    'current washes count: {}, washes offset: {}'
                    .format(washesFromRobot, self._washesCount))
                self._washesOffset = self._washesCount
                self._washesCount = washesFromRobot
                if washesFromRobot > 0:
                    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    self._log.warning(
                        self.description +
                        'Manual usages are registered: from {} to {}, {} times.'
                        .format(self._lastUpdate, now, str(washesFromRobot)))
                    self._manualUsageCount += washesFromRobot
        else:
            self._log.error(self.description + 'leisuWash.getWashesTotalNumber() -> None.')

    def getLastSensorsState(self):
        return self.leisuWash.getLastSensorsState()

    def getCarPosition(self):
        return self.leisuWash.getCarPosition()

    def resetCarPosition(self):
        self._log.info(self.description + 'reset car inside.')
        self.leisuWash.resetCarPosition()

    def inErrorState(self):
        return self._err

    def isConnected(self):
        return self._acc

    def getYellowZoneLength(self):
        return self.carsQueue.getYellowZoneLength()

    def finishWashing(self):
        self.carsQueue.finishWashing()
