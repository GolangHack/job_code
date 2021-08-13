# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging
import pyutils
import threading


class PageBillDispenserTakeChange(HtmlPage):
    def onButtonClick(self, button, arg):
        pass

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        print('PageBillDispenserTakeChange Enter page')
        self.operationScenario = self.getVariable('operationScenario')

        def _dispenseChange():
            print('PageBillDispenserTakeChange._dispenseChange()')
            self.operationScenario.dispenseChange()
            self.operationScenario.checkProcessing()

        threading.Thread(target=_dispenseChange).start()

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print('PageBillDispenserTakeChange Exit page')
