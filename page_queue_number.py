# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from threading import Timer
from operation_scenario import OperationScenario
import logging

class PageQueueNumber(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "main":
            self._timer.cancel()
            self.switchTo("PageMain")

    def preEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.setVariable(robot_number=self.operationScenario.getRobotNumber())
        self.setVariable(queue_number=self.operationScenario.getQueueNumber())
        self.setVariable(qrcode=self.operationScenario.getQrCodeBase64())

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")

        def timeout():
            self.switchTo("PageMain")
        self._timer = Timer(60, timeout)
        self._timer.start()

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")

