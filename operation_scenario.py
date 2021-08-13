# -*- coding: utf-8 -*-
import logging
import random
import time

from calendarEvents import CalendarEvents
import data_storage.database as db
from data_storage.database import Telephone
from smsgate.Gate import Gate
from threading import Thread
import base64
import uuid
import requests
import json
import qrcode
import cStringIO
from requests.exceptions import ConnectionError, Timeout

import random
from datetime import datetime
random.seed(datetime.now())
log = logging.getLogger(__name__)


class OperationScenario(object):
    PAY_DEST_ROBOT='robot'
    PAY_DEST_CLIENT_CARD_FILL='client_card_fill'
    PAY_DEST_EXCHANGE='exchange'
    PAY_DEST_CLIENT_CARD_BUY='client_card_buy'
    # Тип назначения: ручная мойка
    PAY_DEST_CLIENT_MANUAL_WASH='manual_wash'

    PAY_SOURCE_CASH='cash'
    PAY_SOURCE_BANK_CARD='bank_card'
    PAY_SOURCE_CLIENT_CARD='client_card'
    PAY_SOURCE_QR_CODE='qr_code'

    CARD_TYPE_BANK = 'bank_card'
    CARD_TYPE_MIFARE = 'mifare'
    CARD_TYPE_MIFARE_NEW = 'mifare_new'

    CARD_CLOSE_PURPOSE_PAY = 'pay'
    CARD_CLOSE_PURPOSE_SHOW_BALANCE = 'balance'
    CARD_CLOSE_PURPOSE_FILL_CARD = 'fill_card'
    CARD_CLOSE_PURPOSE_BUY_CARD = 'buy_card'
    CARD_CLOSE_PURPOSE_MANUAL_WASH = 'manual_wash'
    CARD_CLOSE_PURPOSE_COMPANY_CHANGE_CARD = 'company_change_card'

    def __init__(self, robotsCount, calendar, vm):
        self.vm = vm
        self.be = self.vm.be
        self.calendar = calendar
        self.robotsCount = robotsCount
        self.robotMaintenance = [0] * self.robotsCount
        self.payDestination = None
        self.payDescription = None
        self.paySource = None
        self.moneyInserted = 0
        self.canGoToSleepMode = None
        'Robot'
        self.robotNumber = None
        self.occupiedRobotsMask = 0
        self.isRobotAllowedHandler_args = []
        self.isRobotAllowedHandler_kwargs = {}
        self.isRobotAllowedHandler = None
        self.queueNumber = 0
        'Program'
        self.programName = None
        self.programNumber = None
        self.programPrice = 0
        self.servicesMask = None
        self.serviceSelected = []
        self.spendingSum = 0
        self.printerFailed = None
        self.wantPrintCheck = False
        self.hasPaper = True

        'Client Card'
        self.cardName = None
        self.clientName = None
        self.clientCard = None
        self.cardPrice = 0
        self.cardUid = None
        self.cardBalance = 0
        self.cardType = None
        self.cardSubType = None
        self.cardInError = False
        self.cardClosePurpose = None

        self.nextPage = None
        self.payHandler = None
        self.updateMoneyHandler = []
        self.updateQueueHandler = []
        self.receiveMoneyEnabled = False
        self.receiveCardsEnabled = False
        self.enableButtonsHandler = []
        self.waitFixedSum = True
        self.errorText = 'empty'

        'PinPad'
        self.updatePincodeMaskHandler = []
        self.pincodeMask = ''

        'Sber QR'
        self.sber_token = None
        self.sber_qr_url = None
        self.sber_qr_order_id = None
        self.sber_qr_order_status = None
        self.pay_qr_temporarily_not_work = None

        'Bill Dispenser'
        self.dispenseBillCount = 0
        self.dispenseBill = 0
        self.dispenseBillHandler = None
        self.noBillDispenser = False
        self.billDispenserFailed = None
        self.billDispenseError = False
        self.billsDispensedCount = 0
        self.billsNotDispensedCount = 0

        'Card Dispenser'
        self.cardDispenserStackLack = False
        self.cardDispenserStackEmpty = False
        self.cardDispenserStackFull = False
        self.cardDispenserFail = False
        self.cardDispenserCheckStatusHandler = None

        'Cashback'
        self.moneyFromCashback = 0
        'Telephone'
        self._telephoneNumber = None
        self._accessCode = None
        self.cardCloseRefuse = False
        self.modeAttachPhone = False
        self.attachPhoneClientName = None
        self.attachPhoneClientAdw = None
        self._isQrReaderLocked = [False] * self.robotsCount

    def finishScenario(self):
        log.info("Finish scenario")
        self.spendingSum = 0
        self.cardBalance = 0
        self.dispenseBillCount = 0
        self.billsDispensedCount = 0
        self.moneyInserted = 0
        self.wantPrintCheck = False
        self.hasPaper = True
        self.payDestination = None
        self.payDescription = ""
        self.programName = None
        self.programNumber = 0
        self.programPrice = 0
        self.billDispenseError = False
        self.paySource = None
        self.serviceSelected = []
        self.moneyFromCashback = 0
        self.unlockAllQrReaders()
        self.canGoToSleepMode = True
        if self.vm.sleep_mode_allowed is True and self.getTimeOfDay() == 'night':
            self.be.switchPageByName("PageSleepMode")
        self.sber_qr_order_status = None

    'Calendar backend'
    def getTimeOfDay(self):
        return self.calendar.getTimeOfDay()

    'Robot backend'
    def registerGetBetterRobotIndexHandler(self, handler):
        self.getBetterRobotIndexHandler = handler

    def registerIsRobotAllowedHandler(self, handler, *args, **kwargs):
        self.isRobotAllowedHandler_args = args
        self.isRobotAllowedHandler_kwargs = kwargs
        self.isRobotAllowedHandler = handler

    def isRobotAllowed(self, index):
        al = True
        if self.isRobotAllowedHandler is not None:
            al = self.isRobotAllowedHandler(index)
        return al

    def getBetterRobotIndex(self, *args, **kwargs):
        return self.getBetterRobotIndexHandler(*args, **kwargs)

    def setSmartSelection(self, state):
        self.smartSelection = state

    def getSmartSelection(self):
        return self.smartSelection

    def setRobotMaintenance(self, robotNumber, mode):
        self.robotMaintenance[robotNumber] = mode

    def getRobotMaintenance(self, robotNumber):
        return self.robotMaintenance[robotNumber]

    'Card dispenser backend'
    def registerCardDispenserCheckStatusHandler(self, handler):
        self.cardDispenserCheckStatusHandler = handler

    def cardDispenserCheckStatus(self):
        import time
        curtime = time.time()
        self.cardDispenserStackEmpty, self.cardDispenserStackLack, self.cardDispenserStackFull, self.cardDispenserFail = self.cardDispenserCheckStatusHandler()
        print "Worked time  cardDispenserCheckStatus %s" % (time.time() - curtime)
    def getCardDispenserStackEmpty(self):
        return self.cardDispenserStackEmpty

    def getCardDispenserStackLack(self):
        return self.cardDispenserStackLack

    def getCardDispenserStackFull(self):
        return self.cardDispenserStackFull

    def isCardDispenserFailed(self):
        return self.cardDispenserFail

    'Card reader backend'
    def setCardClosePurpose(self, purpose):
        self.cardClosePurpose = purpose

    def getCardClosePurpose(self):
        return self.cardClosePurpose

    'Bill dispenser backend'
    def registerBillDispenserFailedHandler(self, handler):
        self.billDispenserFailed = handler

    def isBillDispenserFailed(self):
        if self.billDispenserFailed():
            self.noBillDispenser = True
        else:
            self.noBillDispenser = False
        return self.noBillDispenser

    def registerDispenseBillHandler(self, handler):
        self.dispenseBillHandler = handler

    def setBillDispenseResult(self, errorStatus, billsDispensedCount,
                              billsNotDispensedCount):
        self.billDispenseError = errorStatus
        self.billsNotDispensedCount = billsNotDispensedCount
        self.billsDispensedCount = billsDispensedCount

    def getBillDispenseResult(self):
        return (self.billDispenseError, self.billsDispensedCount,
                self.billsNotDispensedCount)

    'Utilities backend'
    def isMoneyEnough(self):
        log.debug(' Type spending: ' +
                      str(type(self.spendingSum)) +
                      ' Spending sum: ' + str(self.spendingSum) +
                      str(type(self.moneyInserted)) + ' Money inserted: ' +
                      str(self.moneyInserted))
        return self.spendingSum <= self.moneyInserted

    def registerEnableButtonsHandler(self,handler):
        self.enableButtonsHandler.append(handler)

    def enableButtons(self, *args, **kwargs):
        for i in range(len(self.enableButtonsHandler)):
            self.enableButtonsHandler[i](*args, **kwargs)

    def registerReceiveMoneyEnabler(self, enabler):
        self.receiveMoneyEnabler = enabler

    def registerReceiveMoneyDisabler(self, disabler):
        self.receiveMoneyDisabler = disabler


    'Cards Backend'
    # создания юрлица
    def registerCreateCompanyCard(self, handler):
        self._createCompanyCard = handler

    def createCompanyCard(self, description):
        self._createCompanyCard(description)

    # получение всех карт для юр. лиц.
    def registerAllCompanyCard(self, handler):
        self._allCompanyCard = handler

    def getAllCompanyCard(self):
        return self._allCompanyCard()

    # Получить отчеты по карте
    def registerGetReportsByCard(self, handler):
        self._getReportsByCard = handler

    # Получить отчеты по клиенту
    def registergetReportsClient(self, handler):
        self._getReportsClient = handler

    def getReportsByClient(self):
        return self._getReportsClient()

    def getReportsByCard(self):
        return self._getReportsByCard()

    def registerCreateReportByCard(self, handler):
        self._createReportByCard = handler

    def createReportByCard(self):
        self._createReportByCard()

    def registerCreateReportByClientId(self, handler):
        self._createReportByClientId = handler

    def createReportByClientId(self):
        self._createReportByClientId()

    def registerSendEasyCompanyReport(self, handler):
        self._sendEasyCompanyReport = handler

    def sendEasyCompanyReport(self, idReport):
        self._sendEasyCompanyReport(idReport, easy=True)

    def enableCardReader(self):
        log.debug("enable cardreader, pay source {}; pay destination {}".format(self.getPaySource(), self.getPayDestination()))
        if self.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD:
            self.sale()
        else:
            self.enableReceiveCards()
        # (self.getPaySource() == OperationScenario.PAY_SOURCE_CLIENT_CARD) or \
        #             (self.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_FILL):

    def registerReceiveCardsEnabler(self, enabler):
        self.receiveCardsEnabler = enabler

    def registerReceiveCardsDisabler(self, disabler):
        self.receiveCardsDisabler = disabler

    def enableReceiveCards(self):
        self.receiveCardsEnabler()
        self.receiveCardsEnabled = True

    def disableReceiveCards(self):
        log.debug("disable cardreader")
        self.receiveCardsDisabler()
        self.receiveCardsEnabled = False

    def registerCardEventHandler(self, handler):
        self.cardEventHandler = handler

    def cardEvent(self, *args, **kwargs):
        self.cardEventHandler(*args, **kwargs)

    def setClientCard(self, card):
        """
        :type card: db.Card.Card
        """
        self.clientCard = card

    def getClientCard(self):
        """
        :rtype db.Card.Card
        :return: карту
        """
        return self.clientCard

    # TODO удалить или заменить
    def setCardName(self, cardName):
        self.cardName = cardName

    def getCardName(self):
        return self.cardName

    def setClientName(self, clientName):
        self.clientName = clientName

    def getClientName(self):
        return self.clientName

    def setCardUid(self, cardUid):
        self.cardUid = cardUid

    def setReportsByClientId(self, clientID):
        self._reportsByClientCard = clientID

    def getClientIdForReports(self):
        return self._reportsByClientCard

    def getCardUid(self):
        return self.cardUid

    def setCardBalance(self, cardBalance):
        self.cardBalance = cardBalance

    def getCardBalance(self):
        return self.cardBalance

    def setCardType(self, cardType):
        self.cardType = cardType

    def getCardType(self):
        return self.cardType

    def setCardSubType(self, cardSubType):
        self.cardSubType = cardSubType

    def getCardSubType(self):
        return self.cardSubType

    def setCardPrice(self, price):
        self.cardPrice = price

    def getCardPrice(self):
        return self.cardPrice

    def setCardInError(self, state):
        self.cardInError = state

    def getCardInError(self):
        return self.cardInError

    def enableReceiveMoney(self):
        self.receiveMoneyEnabler()
        self.receiveMoneyEnabled = True

    def disableReceiveMoney(self):
        self.receiveMoneyDisabler()
        self.receiveMoneyEnabled = False

    def registerUpdateMoneyHandler(self, updateMoneyHandler):
        self.updateMoneyHandler.append(updateMoneyHandler)

    def updateMoneyInserted(self, bill, *args, **kwargs):
        self.moneyInserted += bill
        for i in range(len(self.updateMoneyHandler)):
            self.updateMoneyHandler[i](self.moneyInserted, *args, **kwargs)

    def isBillAllowed(self, bill):
        ''' Should we received requested bill? '''
        if self.spendingSum == 0 or not self.waitFixedSum:
            return True
        change = (self.moneyInserted + bill) - self.spendingSum
        if change > self.vm.getAvailableChange():
            ' have no change to give '
            if self.callbackIfBillRejected is not None:
                self.callbackIfBillRejected()
            return False
        return True

    def getQueueNumber(self):
        return self.queueNumber

    def registerUpdateQueueHandler(self, updateQueue):
        self.updateQueueHandler.append(updateQueue)

    def updateQueue(self, queue, *args, **kwargs):
        self.queueNumber = queue
        for i in range(len(self.updateQueueHandler)):
            self.updateQueueHandler[i](queue, *args, **kwargs)

    def exchange(self):
        # if (self.moneyInserted / self.dispenseBill) !=
        self.dispenseCount = self.moneyInserted / self.dispenseBill
        self.dispenseBillHandler(self.dispenseCount)

    def registerSaleHandler(self, handler):
        self.saleHandler = handler

    def sale(self):
        log.info("Start bank sale")
        self.saleHandler()

    def registerPayHandler(self, payHandler):
        self.payHandler = payHandler

    def pay(self):
        log.info("Processing payment")
        self.payHandler()

    def isChangeRequired(self):
        return (self.moneyInserted > self.spendingSum) and self.waitFixedSum

    def getDispenseBillCount(self):
        return (self.moneyInserted - self.spendingSum) / self.dispenseBill

    def dispenseChange(self):
        self.dispenseBillCount = self.getDispenseBillCount()
        self.dispenseBillHandler(self.dispenseBillCount)

    '''Internal Variables'''
    def initRobot(self, selectedRobot):
        self.setRobotNumber(selectedRobot)
        self.setPayDestination(self.PAY_DEST_ROBOT)
        self.setPayDescription(u'Оплата мойки автомобиля')
        self.setCardClosePurpose(self.CARD_CLOSE_PURPOSE_PAY)
        self.setWaitFixedSum(True)

    def setPayDestination(self, payDestination):
        self.payDestination = payDestination

    def getPayDestination(self):
        return self.payDestination

    def setPayDescription(self, payDescription):
        self.payDescription = payDescription

    def getPayDescription(self):
        return self.payDescription

    def setPaySource(self, paySource):
        self.paySource = paySource

    def getPaySource(self):
        return self.paySource

    def setMoneyInserted(self, money):
        self.moneyInserted = money

    def getMoneyInserted(self):
        return self.moneyInserted

    def setRobotNumber(self, robotNumber):
        self.robotNumber = robotNumber

    def getRobotNumber(self):
        return self.robotNumber

    def setProgramName(self, programName):
        self.programName = programName

    def getProgramName(self):
        return self.programName

    def setProgramNumber(self, programNumber):
        self.programNumber = programNumber

    def getProgramNumber(self):
        return self.programNumber

    def setProgramPrice(self, programPrice):
        self.programPrice = programPrice

    def getProgramPrice(self):
        return self.programPrice

    def setServicesMask(self, servicesMask):
        self.servicesMask = servicesMask

    def getServicesMask(self):
        return self.servicesMask

    def setSpendingSum(self, spendingSum):
        self.spendingSum = spendingSum

    def getSpendingSum(self):
        return self.spendingSum

    def setPrinterFailed(self, printerFailed):
        self.printerFailed = printerFailed

    def getPrinterFailed(self):
        return self.printerFailed

    def setWantPrintCheck(self, wantPrintCheck):
        self.wantPrintCheck = wantPrintCheck

    def getWantPrintCheck(self):
        return self.wantPrintCheck

    def setHasPaper(self, hasPaper):
        self.hasPaper = hasPaper

    def getHasPaper(self):
        return self.hasPaper

    def setOccupiedRobotsMask(self, occupiedRobotsMask):
        self.occupiedRobotsMask = occupiedRobotsMask

    def getOccupiedRobotsMask(self):
        return self.occupiedRobotsMask

    def setNextPage(self, nextPage):
        self.nextPage = nextPage

    def getNextPage(self):
        return self.nextPage

    def setWaitFixedSum(self, state):
        self.waitFixedSum = state

    def getWaitFixedSum(self):
        return self.waitFixedSum

    def setDispenseBill(self, bill):
        self.dispenseBill = bill

    def getDispenseBill(self):
        return self.dispenseBill

    def setServiceSelected(self, services):
        self.serviceSelected = services

    def getServiceSelected(self):
        return self.serviceSelected

    def setMoneyFromCashback(self, money):
        self.moneyFromCashback = money

    def getMoneyFromCashback(self):
        return self.moneyFromCashback

    def generateDescription(self):
        if self.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
            desc = u'{}, робот №{}, {}: {} р.'.format(self.getPayDescription(),
                                                    self.getRobotNumber(),
                                                    self.getProgramName(),
                                                    self.getSpendingSum())
        elif self.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_FILL:
            desc = u'{}'.format(self.getPayDescription())
        else:
            desc = u'{}: {} р.'.format(self.getPayDescription(), self.getSpendingSum())
        return desc

    def getAmountDescription(self):
        return u'Сумма к списанию {} р.'.format(self.spendingSum)

    def isCashPaymentAvailable(self):
        bill_status = self.vm.billAcceptor.getBillAcceptorStatus()
        return not bill_status.error

    '#################################Telephone code payment'
    def setTelephoneNumber(self, telephone):
        self._telephoneNumber = telephone
        print "Set telephone number"

    def generateAccessCodeForPhone(self, retry=False):
        def sendAccessCode():
            gate = Gate(api_login=self.vm.smsGateLogin,
                        api_password=self.vm.smsGatePassword)
            print "code, balance = " + str(gate.balance())
            sended = gate.send(self._telephoneNumber, "Ваш код: " + self._accessCode)

            log.info("status, id, balance = " + str(sended))
            if len(sended) == 3:
                status, id, balance = sended
                dStatus = gate.getStatusDesc(status)
                log.info(dStatus)
                for x in range(5):
                    time.sleep(5)
                    msgStatus = gate.status(id)
                    if len(msgStatus) == 2:
                        print(u"Message status: " + gate.getStatusDesc(msgStatus[1]))
                        if msgStatus[1] == 103:
                            break
                        if msgStatus[1] in gate._errorCode:
                            self.disableAttachPhoneMode()
                            self.clearTelephoneNumber()
                            self.disablePageCardCloseRefuse()
                            self.vm.pageError.show(error_text="SMSGATE: " + gate.getStatusDesc(msgStatus[1]))
                            break

            if len(sended) == 1:
                dStatus = gate.getStatusDesc(sended[0])
                log.info(dStatus)
                self.disableAttachPhoneMode()
                self.clearTelephoneNumber()
                self.disablePageCardCloseRefuse()
                print(u"Ошибка при отправке сообщения: " + dStatus)
                self.vm.pageError.show(error_text="SMSGATE: " + gate.getStatusDesc(sended[0]))


        if retry:
            print("Retry access code")
        else:
            self._accessCode = "".join([str(random.randint(0, 9)) for x in range(5)])
        log.info("AccessCode: " + self._accessCode)
        print("AccessCode: " + self._accessCode)
        if self.vm.enableSmsGatePinCode:
            Thread(target=sendAccessCode).start()
        else:
            print("Sms gate is not enable. Sms will not be send.")

    def compareAccessCode(self, code):
        if self._accessCode == code:
            return True
        else:
            return False

    def isExistPhoneNumber(self):
        if self._telephoneNumber:
            telephone = Telephone.Telephone(self._telephoneNumber)
            return telephone.isTelephoneExist()
        else:
            return False

    def createCardByTelephone(self):
        telephone = Telephone.Telephone(self._telephoneNumber)
        telephone.createCardByPhone(self.attachPhoneClientName, self.attachPhoneClientAdw)

    def validateAccessCode(self, code):
        """простая валидация кода доступа, если не подешел - идет нахрен"""
        if self._accessCode == code:
            return True
        else:
            return False

    def insertCardByTelephone(self):
        """эмулирует вставку карты, после этого можно вызвать событие
        cardEvent на странице card_close и карточка прочитается как клиентска"""
        self.setCardType(OperationScenario.CARD_TYPE_MIFARE)
        telephone = Telephone.Telephone(self._telephoneNumber)
        card = telephone.getCardByPhone()
        self.setCardUid(card.uid)
        self.setClientCard(card)
        self.setCardSubType(card.type)
        self.setCardBalance(card.balance)
        self.setCardName(card.card_name)
        self.setClientName(card.client_name)
        self.enablePageCardCloseRefuse()
        self.clearTelephoneNumber()

    def clearTelephoneNumber(self):
        """Очистка телефонного номера"""
        self._telephoneNumber = None


    def getLicenseTextPersonalDataProcessing(self):
        return self.vm.licenseTextPersonalDataProcessing
    # todo вроде правильно
    def getLicenseTextAdwDataAgreement(self):
        return self.vm.licenseTextAdwDataAgreement

    def getRequestPhoneForClientCardEnabled(self):
        return self.vm.requestPhoneForClientCardEnabled

    'Переключение ввода телефона в режим ввода номера телефона'
    def enableAttachPhoneMode(self):
        """Страница ввода номера становится привязкой его к карте"""
        log.info("enableAttachPhoneMode")
        self.modeAttachPhone = True

    def disableAttachPhoneMode(self):
        log.info("disableAttachPhoneMode")
        self.modeAttachPhone = False

    'Восстановление после привязки номера телефона к карте'
    def enablePageCardCloseRefuse(self):
        log.info("enablePageCardCloseRefuse")
        self.cardCloseRefuse = True

    def disablePageCardCloseRefuse(self):
        log.info("disablePageCardCloseRefuse")
        self.cardCloseRefuse = False

    'Привязка телефона к карте'
    def attachPhoneNameAdwToCard(self, name, adw):
        self.attachPhoneClientName = name
        self.attachPhoneClientAdw = adw

    'Сохранение номера в базу данных'
    def attachPhoneSave(self):
        self.clientCard.attachPhone(self._telephoneNumber)
        self.clientCard.attachName(self.attachPhoneClientName)
        self.clientCard.attachClientName(self.attachPhoneClientName)
        self.clientCard.setProperty("adw_enabled", self.attachPhoneClientAdw, create=True)

    def isPhoneBinded(self):
        """Привязан ли телефон к карте?"""
        if self._telephoneNumber:
            telephone = Telephone.Telephone(self._telephoneNumber)
            return telephone.isTelephoneExist()
        else:
            raise Exception("Нужно сначала установить номер перед вызовом этой функции")

    'Если пользователь выбрал больше не справшивать'
    def enableSkipCardRequest(self):
        self.clientCard.setProperty("request_enter_phone_enabled", "False", create=True)

    '#################################QR Code'
    def getQrCodeBase64(self):
        if (self.getPaySource() == OperationScenario.PAY_SOURCE_CASH or
               self.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD):
            if self.vm.isKkmFiscal:
                return self.vm.getLastCheckQRCode()
            else:
                log.warning(u"Казначей не фискализирован. Будет показан QR содержащий текст 'Thank you for payment!'")
                return self.vm.getThankQRCode()
        else:
            return self.vm.getThankQRCode()

    def getDryZoneDisabled(self):
        return self.vm.dryZoneDisabled

    'Режим работы только qr коды'
    def atolModeOnlyQrCodeCheck(self):
        return self.vm.atol_mode_only_qr_code_check

    def checkProcessing(self):
        dispenseError, billsDispensed, billsNotDispensed = self.getBillDispenseResult()

        def checkProcessingWithoutPrint():
            self.setWantPrintCheck(False)
            self.pay()
            if dispenseError is False:
                if self.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                    self.unlockQrReader(self.robotNumber - 1)
                    self.be.switchPageByName("PageQueueNumber")
                else:
                    self.be.switchPageByName("PageQRCode")
            else:
                self.be.switchPageByName("PageErrorBillAcceptor")

        if self.vm._atol_disabled or self.atolModeOnlyQrCodeCheck() or self.vm.fiskal_check_disabled:
            checkProcessingWithoutPrint()
        else:
            if dispenseError is False:
                if self.getHasPaper():
                    self.be.switchPageByName("PageWantPrint")
                else:
                    checkProcessingWithoutPrint()
            else:
                checkProcessingWithoutPrint()

    def getIsPinPadAviailable(self):
        return self.vm.isPinPadAvailable

    def billDispenserClearTopFloat(self):
        """Очистить верхник отсек купюроразменника (сбросить вниз его)"""
        self.vm.billAcceptor.emptyStorage()

    def registerCallbackIfBillRejected(self, callback):
        """Если не можем дать сдачи с запрашиваемой купюры - то выполнить кэллбек"""
        self.callbackIfBillRejected = callback

    def checkHasPaper(self):
        return self.vm.checkHasPaper()

    def refreshBillDispenserStatus(self):
        self.vm.billDispenser.testDispense()

    def choiceRobot(self, robotID):
        """
        Сценарий после нажатия на кнопку выбора, или оплаты
        RobotID - робот 1 это robotID 0, робот 2 это robotID 1 и т.д.
        :return True если успешно, False - если ошибка
        """
        allowed = self.isRobotAllowed(robotID-1)
        maintenance = self.getRobotMaintenance(robotID-1)
        if (not allowed) or (maintenance == 1):
            print(u"Робот не доступен")
            self.be.switchPageByName("PageError", error_text=u"Этот робот не доступен в данный момент.")
            return False
        "Умный выбор"
        if not self.getSmartSelection():
            selectedRobot = robotID
        else:
            selectedRobot = self.getBetterRobotIndex()
        "Инициация робота"
        self.initRobot(selectedRobot)

        if selectedRobot is None:
            print(u"Все мойки в данный момент заняты")
            self.be.switchPageByName("PageError", error_text=u'Все мойки в данный момент заняты')
            return False
        return True

    def lockQrReader(self, index):
        self._isQrReaderLocked[index] = True

    def unlockQrReader(self, index):
        self._isQrReaderLocked[index] = False

    def unlockAllQrReaders(self):
        for i in range(self.robotsCount):
            self._isQrReaderLocked[i] = False

    def isQrReaderLocked(self, index):
        return self._isQrReaderLocked[index]

    def getSberAccessToken(self, scope):
        client_id = self.vm.sber_client_id
        client_secret = self.vm.sber_client_secret
        id_secret = '{client_id}:{client_secret}'.format(client_id=client_id, client_secret=client_secret)
        base_id_secret = base64.b64encode(id_secret)
        operation_rquid = uuid.uuid4().hex
        data = "grant_type=client_credentials&scope={scope}".format(scope=scope)
        headers = {
            'x-ibm-client-id': "{client_id}".format(client_id=client_id),
            'authorization': "Basic {base_id_secret}".format(base_id_secret=base_id_secret),
            'rquid': "{operation_rquid}".format(operation_rquid=operation_rquid),
            'content-type': "application/x-www-form-urlencoded",
            'accept': "application/json"
        }
        try:
            request = requests.post("https://open.api.sberbank.ru/ru/prod/tokens/v2/oauth",
                                    data=data, headers=headers, timeout=10)
            response = json.loads(request.text)
            if 'access_token' in response:
                self.sber_token = response['access_token']
                return self.sber_token
            else:
                log.error('QR Token receiving error. Error Code {}: {}, {}'.format(response['httpCode'], response['httpMessage'], response['moreInformation']))
                return None
        except (ConnectionError, Timeout):
            log.error('QR Token receiving error. Connection Error')
            return None

    def getSberQrUrl(self):
        client_id = self.vm.sber_client_id
        operation_rquid = uuid.uuid4().hex
        now = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
        member_id = self.vm.sber_member_id
        order_number = uuid.uuid4().hex
        id_qr = self.vm.sber_id_qr
        summ = self.getSpendingSum() * 100
        data = '{"rq_uid":"' + operation_rquid + '",' \
               '"rq_tm":"' + now + '",' \
               '"member_id":"' + member_id + '",' \
               '"order_number":"' + str(order_number) + '",' \
               '"order_create_date":"' + now + '",' \
               '"order_params_type":[{"position_name":"Washing payment",' \
                                    '"position_count":1,' \
                                    '"position_sum":' + str(summ) + ',' \
                                    '"position_description":"Washing payment"}],' \
               '"id_qr":"' + id_qr + '",' \
               '"order_sum":' + str(summ) + ',' \
               '"currency":"643",' \
               '"description":"Washing payment"}'
        headers = {
            'x-ibm-client-id': "{client_id}".format(client_id=client_id),
            'authorization': "Bearer {token}".format(token=self.sber_token),
            'x-Introspect-RqUID': "{operation_rquid}".format(operation_rquid=operation_rquid),
            'content-type': "application/json",
            'accept': "application/json"
        }
        try:
            request = requests.post("https://open.api.sberbank.ru/ru/prod/order/v1/creation", data=data, headers=headers)
            response = json.loads(request.text)
            if 'status' in response:
                try:
                    self.sber_qr_url = response['status']['order_form_url']
                    self.sber_qr_order_id = response['status']['order_id']
                    log.info('QR Order is generated. QR URL: {}, Order ID: {}'.format(self.sber_qr_url, self.sber_qr_order_id))
                except KeyError:
                    log.error('QR Error in ordering. Unknown error: {}'.format(response))
                    return None
            else:
                self.sber_qr_url = None
                log.error('QR Error in ordering. Error Code {}: {}, {}'.format(response['httpCode'], response['httpMessage'], response['moreInformation']))
                print 'Error in ordering: ', response['httpCode'], response['httpMessage'], response['moreInformation']
        except ConnectionError:
            log.error('QR Error in ordering. Connection error')
            return None

    def getStatusSberQrOrder(self, order_id):
        client_id = self.vm.sber_client_id
        operation_rquid = uuid.uuid4().hex
        now = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
        data = '{"rq_uid":"' + operation_rquid + '",' \
               '"rq_tm":"' + now + '",' \
               '"order_id":"' + str(order_id) + '"}'
        headers = {
            'x-ibm-client-id': "{client_id}".format(client_id=client_id),
            'authorization': "Bearer {token}".format(token=self.sber_token),
            'x-Introspect-RqUID': "{operation_rquid}".format(operation_rquid=operation_rquid),
            'content-type': "application/json",
            'accept': "application/json"
        }
        try:
            request = requests.post("https://open.api.sberbank.ru/ru/prod/order/v1/status",
                                    data=data, headers=headers, timeout=10)
            response = json.loads(request.text)
            if 'status' in response:
                try:
                    if response['status']['order_state'] != self.sber_qr_order_status:
                        log.info('QR Order status: {}'.format(response['status']['order_state']))
                        print 'QR Order status: ' + response['status']['order_state']
                    self.sber_qr_order_status = response['status']['order_state']
                    return response['status']['order_state']
                except KeyError:
                    log.error('QR Error getting order status. Unknown error: {}'.format(response))
                    return None
            else:
                log.error('QR Error getting order status. Error Code {}: {}, {}'.format(response['httpCode'], response['httpMessage'], response['moreInformation']))
                print 'Error in getting qr order status: ', response['httpCode'], response['httpMessage'], response['moreInformation']
                return None
        except (ConnectionError, Timeout):
            log.error('QR Error getting order status. Connection error')
            return None

    def closeSberQrOrder(self, order_id):
        client_id = self.vm.sber_client_id
        operation_rquid = uuid.uuid4().hex
        now = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
        data = '{"rq_uid":"' + operation_rquid + '",' \
               '"rq_tm":"' + now + '",' \
               '"order_id":"' + str(order_id) + '"}'
        headers = {
            'x-ibm-client-id': "{client_id}".format(client_id=client_id),
            'authorization': "Bearer {token}".format(token=self.sber_token),
            'x-Introspect-RqUID': "{operation_rquid}".format(operation_rquid=operation_rquid),
            'content-type': "application/json",
            'accept': "application/json"
        }
        try:
            request = requests.post("https://open.api.sberbank.ru/ru/prod/order/v1/revocation", data=data, headers=headers)
            response = json.loads(request.text)
            if 'status' in response:
                try:
                    if response['status']['order_state'] != self.sber_qr_order_status:
                        log.info('QR Close order status: {}'.format(response['status']['order_state']))
                        print 'QR Close order status: ' + response['status']['order_state']
                    self.sber_qr_order_status = response['status']['order_state']
                    return response['status']['order_state']
                except KeyError:
                    log.error('QR Error getting order status. Unknown error: {}'.format(response))
            else:
                log.error('QR Error getting order status. Error Code {}: {}, {}'.format(response['httpCode'], response['httpMessage'], response['moreInformation']))
                print 'Error in getting qr order status: ', response['httpCode'], response['httpMessage'], response['moreInformation']
                return None
        except ConnectionError:
            log.error('QR Error getting order status. Connection error')
            return None

    def getSberQrCodeInBase64(self):
        qr = qrcode.QRCode(version=3)
        qr.add_data(self.sber_qr_url)
        qr.make()
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = cStringIO.StringIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue())
        return img_base64

    def pushPincodeMask(self):
        self.pincodeMask += '*'

    def popPincodeMask(self):
        self.pincodeMask = self.pincodeMask[:-1]

    def clearPincodeMask(self):
        self.pincodeMask = ''

    def registerUpdatePincodeMaskHandler(self, pincodeMaskHandler):
        self.updatePincodeMaskHandler.append(pincodeMaskHandler)

    def updatePincodeMask(self):
        for i in range(len(self.updatePincodeMaskHandler)):
            self.updatePincodeMaskHandler[i](self.pincodeMask)
