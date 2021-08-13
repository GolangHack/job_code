# -*- coding: utf-8 -*-
import threading
import time

from htmlpy_core.html_page import HtmlPage
from threading import Timer
from operation_scenario import OperationScenario
import logging

log = logging.getLogger(__name__)


class PageWantPrint(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "print":
            self.operationScenario.setWantPrintCheck(True)
            self.switchTo("PageCheckPrinting")
        elif button == "skip":
            log.info("Refuse printing")
            self.operationScenario.setWantPrintCheck(False)
            print("Payment without printing check")
            self.operationScenario.pay()
            if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                self.switchTo("PageQueueNumber")
            else:
                self.switchTo("PageQRCode")

    def onEnter(self, prevPage, *args, **kwargs):
        log.info("Enter page")
        "Если режим только qr чеки, то даже не спраивать"
        self.operationScenario = self.getVariable('operationScenario')

    def onExit(self, nextPage, *args, **kwargs):
        log.info("Exit page")
