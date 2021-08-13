# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
#from threading import Timer
from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging

class PageExchange(HtmlPage):

    def __init__(self, *args, **kwargs):
        super(PageExchange, self).__init__(*args, **kwargs)
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.registerUpdateMoneyHandler(self.updateMoney)
        self.operationScenario.registerEnableButtonsHandler(self.enableButtons)

    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")
        elif button == "exchange":
            self.operationScenario.exchange()
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario.enableReceiveMoney()
        self.setVariable(to_pay = self.operationScenario.getSpendingSum())

        logging.getLogger(__name__).info("Enter page")
        print "enter exchange page"

    def onExit(self, nextPage, *args, **kwargs):
        self.operationScenario.disableReceiveMoney()
        logging.getLogger(__name__).info("Exit page")
        print "exit exchange page"

    def updateMoney(self, money):
        print "Update money!", money
        self.changeValueById("sum", money)
        self.setElementEnabled("exchange", True)
        self.setElementEnabled("main", False)

    def enableButtons(self, state):
        self.setElementEnabled("exchange", state)
        if state and self.operationScenario.getMoneyInserted() == 0:
            self.setElementEnabled("main", state)
