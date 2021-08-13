# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
#from threading import Timer
from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging

class PageBillDispenserFailed(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "next":
            self.switchTo("PagePayCash")
        elif button == "main":
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        if self.operationScenario.atolModeOnlyQrCodeCheck():
            self.changeElementVisibility(id='paper_is_out', visible=False)
        else:
            isPaperOut = not self.operationScenario.checkHasPaper()
            self.operationScenario.setHasPaper(not isPaperOut)
            self.changeElementVisibility(id='paper_is_out', visible=isPaperOut)
        logging.getLogger(__name__).info("Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        # self.operationScenario.pay()
        logging.getLogger(__name__).info("Exit page")
