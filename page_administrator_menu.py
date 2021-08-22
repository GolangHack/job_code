# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
import os


class PageAdministartorMenu(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")
        if button == "toConfig":
            self.switchTo("PageConfigEditor")
        if button == "toChangeCardForCompany":
            self.operationScenario.setPayDescription(u'Перевести карту из физ лица в юридическое лицо')
            self.operationScenario.setCardClosePurpose(OperationScenario.CARD_CLOSE_PURPOSE_COMPANY_CHANGE_CARD)
            self.switchTo("PageCardClose", card_type=u"клиентскую")
        if button == "toReportControl":
            self.switchTo("PageReportControl")
        if button == "toBillDispenserActions":
            self.switchTo("PageAdministartorMenuBillAcceptorAndDispenser")
        if button == "updates":
            self.switchTo("PageUpdater")

    def preEnter(self, previousPage, *args, **kwargs):
        try:
            with open("{}/updater/currently_version".format(os.path.expanduser("~"))) as currently_version_file:
                currently_version = currently_version_file.read()
            with open("{}/updater/actual_version".format(os.path.expanduser("~"))) as actual_version_file:
                actual_version = actual_version_file.read()
            self.setVariable(versions=u"Текущая версия ПО: {} Актуальная версия ПО: {}".format(currently_version, actual_version))
            if int(currently_version) < int(actual_version):
                self.setVariable(must_update=True)
            else:
                self.setVariable(must_update=False)
        except IOError:
            self.setVariable(must_update=False)
            logging.error(u'Не найден файл currently_version и/или actual_version')

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.finishScenario()
        # TODO
        self.setVariable(billAcceptorTypename=self.operationScenario.vm.billAcceptorTypename)

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print "exit PageAdministartorMenu"
