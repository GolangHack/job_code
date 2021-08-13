# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from threading import Timer
from operation_scenario import OperationScenario
import logging

class PageAddPhoneInCard(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "attach":
            self.operationScenario.enableAttachPhoneMode()
            self.switchTo("PageInputPhone", cardAttach=True)
        elif button == "skip":
            if arg == "true":
                self.operationScenario.enableSkipCardRequest()
            self.operationScenario.enablePageCardCloseRefuse()
            self.switchTo("PageCardClose")


    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.disableReceiveCards()

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
