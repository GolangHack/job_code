# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from threading import Timer
from operation_scenario import OperationScenario
import logging


class PageInputPhone(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "next":
            self.operationScenario.setTelephoneNumber(self.code_phone_counrty + self.inputValue)
            if self.operationScenario.modeAttachPhone:
                if self.operationScenario.isPhoneBinded():
                    self.switchTo("PageErrorPhoneIsBinded")
                else:
                    self.switchTo("PageInputName")
            else:
                if self.operationScenario.isExistPhoneNumber():
                    # Отправить код здесь
                    self.operationScenario.generateAccessCodeForPhone()
                    self.switchTo("PageInputAccessCode")
                else:
                    self.switchTo("PageInputName")
        elif button == "main":
            self.operationScenario.clearTelephoneNumber()
            self.operationScenario.disableAttachPhoneMode()
            self.operationScenario.disablePageCardCloseRefuse()
            self.switchTo("PageMain")
        elif button == "backspace":
            self.inputValue = self.inputValue[:-1]
            print "Value",  self.inputValue
            self.changeValueById('input_value', self.inputValue)
        else:
            char = button.split("_")[1]
            if len(self.inputValue) == 0 and char == "0":
                self.inputValue += ""
            elif len(self.inputValue) == self.lenghtPhoneNumber:
                self.inputValue += ""
            else:
                self.inputValue += char
            # print "Input Value", self.inputValue
            self.changeValueById('input_value', self.inputValue)
        if len(self.inputValue) == self.lenghtPhoneNumber:
            self.setElementEnabled("next", True)
        else:
            self.setElementEnabled("next", False)

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.disableReceiveCards()
        self.code_phone_counrty = self.getVariable('code_phone_counrty')
        self.lenghtPhoneNumber = self.getVariable('lenght_phone_number')
        self.inputValue = ''
        self.setElementEnabled("next", False)

    def onExit(self, nextPage, *args, **kwargs):
        pass
