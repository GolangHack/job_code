# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
#from threading import Timer
from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging
import config

class PageBankExchange(HtmlPage):

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        logging.getLogger(__name__).info("Enter page")

        def wait_some():
            print ("PageBankExchange, waint_some (call checkProcessing)")
            # Устанавливаем нужную сумму денег
            self.operationScenario.moneyInserted = self.operationScenario.spendingSum
            self.operationScenario.checkProcessing()

        if (config.getProperty('debug_emualete_bank_card', default=False, _type='bool')) and \
                (self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD):
            Delay.once(self, 2, wait_some)

        def getSberQrAndSwitchPage():
            self.operationScenario.sber_qr_order_id = None
            self.operationScenario.getSberAccessToken(scope='https://api.sberbank.ru/order.create')
            self.operationScenario.getSberQrUrl()
            if self.operationScenario.sber_qr_url is not None:
                self.switchTo("PagePayQr")
            else:
                self.operationScenario.pay_qr_temporarily_not_work = True
                self.changeValueById('message', u'Извините, сервис временно недоступен')
                # Timer(2, self.switchTo("PageSelPay")).start()
                Delay.once(self, 2, getSberQrAndSwitchPage)

        if self.getVariable('pay_qr_enabled') and (
            self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_QR_CODE):
            #Timer(0.1, getSberQrAndSwitchPage).start()
            Delay.once(0.1, getSberQrAndSwitchPage)

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")

   
