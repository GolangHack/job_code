# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from threading import Timer
from operation_scenario import OperationScenario
import logging

class PageInputSum(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "next":
            if (self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD) or \
                    (self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_CLIENT_CARD):
                try:
                    self.operationScenario.setSpendingSum(int(self.inputValue))
                    self.switchTo("PageCardClose", card_type=u"банковскую",
                                  amount_desc=self.operationScenario.getAmountDescription())
                except ValueError:
                    pass
            if self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_QR_CODE:
                try:
                    self.operationScenario.setSpendingSum(int(self.inputValue))
                    self.operationScenario.setMoneyInserted(self.operationScenario.getSpendingSum())
                    self.switchTo("PageBankExchange")
                except ValueError:
                    pass
        elif button == "main":
            self.switchTo("PageMain")
        elif button == "backspace":
            self.inputValue = self.inputValue[:-1]
            print "Value",  self.inputValue
            self.changeValueById('input_value', self.inputValue)
        else:
            char = button.split("_")[1]
            if self.operationScenario.getIsPinPadAviailable():
                if (len(self.inputValue) == 0 and char == "0") or ():
                    self.inputValue += ""
                else:
                    self.inputValue += char
            else:
                if (len(self.inputValue) == 0 and char == "0") or \
                        (len(self.inputValue) == self.operationScenario.vm.input_sum_limit):
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
