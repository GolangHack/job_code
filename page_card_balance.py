# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging

class PageCardBalance(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.changeValueById('uid', self.operationScenario.getCardUid())
        self.changeValueById('name', self.operationScenario.getCardName())
        self.changeValueById('balance', self.operationScenario.getCardBalance())

    def onExit(self, nextPage, *args, **kwargs):
        pass
