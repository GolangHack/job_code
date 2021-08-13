# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging

class PagePayCash(HtmlPage):

    def __init__(self, *args, **kwargs):
        super(PagePayCash, self).__init__(*args, **kwargs)
        self._paymentEmulate = self.getVariable('paymentEmulate')
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.registerUpdateMoneyHandler(self.updateMoney)
        self.operationScenario.registerEnableButtonsHandler(self.enableButtons)
        self.operationScenario.registerCallbackIfBillRejected(self.billRejected)

    def billRejected(self):
        """Не могу дать сдачи с такой купюры"""
        self.changeValueById("message", u"Нет возможности выдать сдачу, внесите купюру меньшего номинала")

    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")
        elif button == "pay":
            if self.operationScenario.isChangeRequired():
                self.switchTo("PageBillDispenserTakeChange")
            else:
                self.operationScenario.checkProcessing()

    def preEnter(self, previousPage, *args, **kwargs):
        if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
            self.setVariable(fill_cash_header = u'Требуется внести')
            self.setVariable(currency = u' р.')
            self.setVariable(to_pay = self.operationScenario.getSpendingSum())
        elif self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_FILL:
            self.setVariable(fill_cash_header = u'Пополнение клиентской карты')
            self.setVariable(currency = u'')
            self.setVariable(to_pay = '')
        elif self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_BUY:
            self.setVariable(fill_cash_header = u'Покупка клиентской карты')
            self.setVariable(currency = u' р.')
            self.setVariable(to_pay = self.operationScenario.getSpendingSum())
        elif self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_MANUAL_WASH:
            self.setVariable(fill_cash_header=u'Требуется внести')
            self.setVariable(currency=u'р.')
            self.setVariable(to_pay=self.operationScenario.getSpendingSum())

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario.canGoToSleepMode = False
        self.operationScenario.enableReceiveMoney()

        if self._paymentEmulate:
            def paySome():
                self.operationScenario.updateMoneyInserted(self.operationScenario.getSpendingSum())

            def refillCard():
                self.operationScenario.updateMoneyInserted(400)

            if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_FILL:
                Timer(1, refillCard).start()
            else:
                Timer(2, paySome).start()
        logging.getLogger(__name__).info("Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        self.operationScenario.disableReceiveMoney()
        print("Payment cash disable cardReceive")
        logging.getLogger(__name__).info("Exit page")

    def updateMoney(self, money):
        self.changeValueById("sum", money)
        if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_FILL:
            # moneyToFill = self.operationScenario.getSpendingSum()
            self.operationScenario.setSpendingSum(money)
            self.setElementEnabled("pay", True)
        else:
            if self.operationScenario.isMoneyEnough():
                self.setElementEnabled("pay", True)
        self.setElementEnabled("main", False)

    def enableButtons(self, state):
        self.changeValueById("message",
                             u"")
        if self.operationScenario.isMoneyEnough():
            self.setElementEnabled("pay", state)
        if state and self.operationScenario.getMoneyInserted() == 0:
            self.setElementEnabled("main", state)
