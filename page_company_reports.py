# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
import config
import json
import database


class PageCompanyReports(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")
        if button == "toAdministrationMenu":
            self.switchTo("PageAdministartorMenu")
        if button == "createReport":
            self.operationScenario.createReportByClientId() # getReportsByClientId
            self.switchTo("PageCompanyReports")
        if button == "sendEasyReport":
            self.operationScenario.sendEasyCompanyReport(arg)

    def preEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        reports = self.operationScenario.getReportsByClient()
        self.operationScenario.finishScenario()
        self.setVariable(reports=reports,
                         uid=self.operationScenario.getCardUid())

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        print "enter PageCompanyReports"

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print "exit PageCompanyReports"
