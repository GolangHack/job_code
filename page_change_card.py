# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
import config
import json
import database
log = logging.getLogger(__name__)

class PageChangeCard(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")
        if button == "toConfig":
            self.switchTo("PageConfigEditor")
        if button == "saveCompanyCard":
            uid = self.operationScenario.getCardUid()
            self.operationScenario.createCompanyCard(arg)
            log.info(u"Карта с uid %s стала юридической, с описание конторы:", uid)
            log.info(arg)
            self.switchTo("PageAdministartorMenu")

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.finishScenario()
        self.setVariable(operationScenario=self.operationScenario)


    def onExit(self, nextPage, *args, **kwargs):
        log.info("Exit page")
        print "exit PageChangeCard"
