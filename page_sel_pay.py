# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
import config
from pyutils.checkInternet import checkInternet


class PageSelPay(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "cash":
            self.operationScenario.setPaySource(OperationScenario.PAY_SOURCE_CASH)
            if self.operationScenario.isBillDispenserFailed() and self.operationScenario.getPayDestination() != OperationScenario.PAY_DEST_CLIENT_CARD_FILL:
                self.switchTo("PageWarning", next="PagePayCash",
                              warning_text=u'В данный момент отсутствует возможность выдачи сдачи.<br>'
                                           u'Хотите продолжить?')
            else:
                self.switchTo("PagePayCash")
        elif button == "bank_card":
            self.operationScenario.setPaySource(OperationScenario.PAY_SOURCE_BANK_CARD)
            if self.operationScenario.getWaitFixedSum():
                self.switchTo("PageCardClose", card_type=u"банковскую",
                              amount_desc=self.operationScenario.getAmountDescription())
            else:
                self.switchTo("PageInputSum")
        elif button == "client_card":
            self.operationScenario.setPaySource(OperationScenario.PAY_SOURCE_CLIENT_CARD)
            if self.operationScenario.getWaitFixedSum():
                self.switchTo("PageCardClose", card_type=u"клиентскую")
            else:
                self.switchTo("PageInputSum")
        elif button == "number_telephone":
            # todo уточнить мб тип платежа телефонный номер?
            self.operationScenario.setPaySource(OperationScenario.PAY_SOURCE_CLIENT_CARD)
            self.switchTo("PageInputPhone")
        elif button == "qr_code":
            self.operationScenario.setPaySource(OperationScenario.PAY_SOURCE_QR_CODE)
            if self.operationScenario.getWaitFixedSum():
                self.switchTo("PageBankExchange")
            else:
                self.switchTo("PageInputSum")
        elif button == "main":
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        if self.getVariable('pay_bank_disabled') or not checkInternet():
            self.setElementEnabled("bank_card", False)
            if config.getProperty("debug_emualete_bank_card", default=False, _type='bool'):
                self.setElementEnabled("bank_card", True)

        if self.getVariable('pay_cash_disabled') or not self.operationScenario.isCashPaymentAvailable():
            self.setElementEnabled("cash", False)

        if self.getVariable('pay_client_card_disabled'):
            self.setElementEnabled("client_card", False)

        if (self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_BUY):
            self.setElementEnabled("client_card", False)

        if (self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_FILL):
            self.setElementEnabled("client_card", False)

        if (self.operationScenario.getPayDestination() == self.operationScenario.PAY_DEST_CLIENT_MANUAL_WASH):
            self.setElementEnabled("client_card", False)

        if self.operationScenario.pay_qr_temporarily_not_work is True or not checkInternet():
            self.setElementEnabled("qr_code", False)

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
