# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from threading import Timer
from operation_scenario import OperationScenario
import logging

class PageCheckPrinting(HtmlPage):

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')

        def wait_some():
            print "Payment with printing check"
            self.operationScenario.pay()

            if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                self.switchTo("PageQueueNumber")
            else:
                self.switchTo("PageQRCode")
        Timer(1, wait_some).start()

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print "exit check printing page"
