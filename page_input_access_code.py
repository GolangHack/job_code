# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
#from threading import Timer
from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging

class PageInputAccessCode(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "nextTo":
            if self.operationScenario.validateAccessCode(self.inputValue):
                'Привязать телефон к карте или создать с нуля телефонный номер, если его нет в базе данных'
                if self.operationScenario.modeAttachPhone:
                    self.operationScenario.disableAttachPhoneMode()
                    self.operationScenario.attachPhoneSave()
                if not self.operationScenario.isPhoneBinded():
                    self.operationScenario.createCardByTelephone()
                self.operationScenario.insertCardByTelephone()
                self.switchTo("PageCardClose")
            else:
                self.switchTo("PageNotCorrectPincode")

        elif button == "send_recent":
            self.operationScenario.generateAccessCodeForPhone()
            self._resetTimerTrailsEnterPinCode()
        elif button == "main":
            self.operationScenario.clearTelephoneNumber()
            self.operationScenario.disablePageCardCloseRefuse()
            self.operationScenario.disableAttachPhoneMode()
            self.switchTo("PageMain")
        elif button == "backspace":
            self.inputValue = self.inputValue[:-1]
            print "Value",  self.inputValue
            self.changeValueById('input_value', self.inputValue)
        else:
            char = button.split("_")[1]
            if len(self.inputValue) > 4:
                self.inputValue += ""
            else:
                self.inputValue += char
            # print "Input Value", self.inputValue
            self.changeValueById('input_value', self.inputValue)
        if len(self.inputValue) > 4:
            self.setElementEnabled("nextTo", True)
        else:
            self.setElementEnabled("nextTo", False)

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.inputValue = ''
        self.setElementEnabled("nextTo", False)
        self._resetTimerTrailsEnterPinCode()
        self.counterTrails = 0

    def _resetTimerTrailsEnterPinCode(self):
        """Включить кнопку по истечению времени"""
        self.setElementEnabled("send_recent", False)
        Timer(30, self._setEnableSendRecent).start()
        print("Disable button send_recent")

    def _setEnableSendRecent(self):
        print("Enable button send_recent")
        self.setElementEnabled("send_recent", True)

    def onExit(self, nextPage, *args, **kwargs):
        pass
