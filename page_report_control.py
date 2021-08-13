# -*- coding: utf-8 -*-
import json
from pprint import pprint
import codecs
import os

import configparser

from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
import config
import json


class PageReportControl(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")
        if button == "toAdministrationMenu":
            self.switchTo("PageAdministartorMenu")
        if button == "toReportsByClientId":
            self.operationScenario.setReportsByClientId(arg)
            self.switchTo("PageCompanyReports")

    def preEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.finishScenario()
        cards = self.operationScenario.getAllCompanyCard()
        self.setVariable(cards=cards)

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        print "enter PageReportControl"

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print "exit PageReportControl"
