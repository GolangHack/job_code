# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from threading import Thread
from operation_scenario import OperationScenario
from pyutils.delay import Delay
import logging
import socket
import urllib2
import time


class PagePayQr(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "main":
            Thread(target=self.closePageAndCloseOrder).start()

    def preEnter(self, previousPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.setVariable(qrcode=self.operationScenario.getSberQrCodeInBase64())
        self.operationScenario.getSberAccessToken(scope='https://api.sberbank.ru/order.status')
        self.setVariable(to_pay=self.operationScenario.getSpendingSum())

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario.canGoToSleepMode = False
        self.delayCheckSberQrStatus = Delay.periodic(2, self.checkSberQrStatus)
        self.sberQrId = self.operationScenario.sber_qr_order_id
        sberQrStatus = self.operationScenario.getStatusSberQrOrder(self.sberQrId)
        if sberQrStatus is None:
            self.changeValueById(
                'message', u'Извините, сервис временно недоступен. '
                           u'Вы можете воспользоваться другим способом оплаты.')
            self.changeValueById('qrcode', '')
        self.startTimestamp = int(time.time())

    def checkSberQrStatus(self):
        currTimestamp = int(time.time())
        secondsPassed = currTimestamp - self.startTimestamp
        if 48 <= secondsPassed <= 50:
            self.operationScenario.getSberAccessToken(scope='https://api.sberbank.ru/order.status')
        if secondsPassed >= 90:
            self.handleSberQrError(
                message=u'Сервис в процессе проверки статуса заказа '
                        u'не дождался оплаты и прекратил операцию.')
        if self.operationScenario.sber_qr_url is not None:
            sberQrStatus = self.operationScenario.getStatusSberQrOrder(self.sberQrId)
            if sberQrStatus is None:
                self.handleSberQrError(
                    message=u'Произошла потеря соединения. '
                            u'Пожалуйста, выберите другой способ оплаты.'
                            u'<br>Если вы уже оплатили заказ и мойка не '
                            u'началась, пожалуйста, обратитесь к '
                            u'администратору для возврата средств.')
            elif sberQrStatus == 'PAID':
                self.operationScenario.checkProcessing()

    def closePageAndCloseOrder(self):
        self.switchTo("PageMain")
        self.operationScenario.getSberAccessToken(scope='https://api.sberbank.ru/order.revoke')
        self.operationScenario.closeSberQrOrder(self.sberQrId)

    def handleSberQrError(self, message):
        logging.getLogger(__name__).warning(message)
        self.changeValueById('qrcode', '')
        self.changeValueById('message', message)
        self.delayCheckSberQrStatus.cancel()

    def onExit(self, nextPage, *args, **kwargs):
        self.delayCheckSberQrStatus.cancel()
        self.operationScenario.sber_qr_url = None
        self.operationScenario.sber_qr_order_status = None
        logging.getLogger(__name__).info("Exit page")
