# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging

class PageWarningDeprecated(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
