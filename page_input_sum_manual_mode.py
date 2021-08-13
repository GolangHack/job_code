# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
#from threading import Timer
from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging


class PageInputSumManualMode(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "next":
            self.operationScenario.setPayDestination(self.operationScenario.PAY_DEST_CLIENT_MANUAL_WASH)
            self.operationScenario.setPayDescription(u"Оплата ручной мойки: "+(self.inputValue))
            self.operationScenario.setSpendingSum(int(self.inputValue))
            self.operationScenario.setWaitFixedSum(True)
            self.switchTo("PageSelPay",
                          pay_description=self.operationScenario.getPayDescription())
        elif button == "main":
            self.switchTo("PageMain")
        elif button == "backspace":
            self.inputValue = self.inputValue[:-1]
            print "Value",  self.inputValue
            self.changeValueById('input_value', self.inputValue)
        else:
            char = button.split("_")[1]
            if len(self.inputValue) == 0 and char == "0":
                self.inputValue += ""
            else:
                self.inputValue += char
            # print "Input Value", self.inputValue
            self.changeValueById('input_value', self.inputValue)

        if len(self.inputValue) > 0:
            self.setElementEnabled("next", True)
        else:
            self.setElementEnabled("next", False)

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.inputValue = ''
        self.setElementEnabled("next", False)

    def onExit(self, nextPage, *args, **kwargs):
        pass
