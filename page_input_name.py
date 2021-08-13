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
import ast


class PageInputName(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "next" or button == "next2":
            # print arg
            print("arg:"+arg)
            newsletter = False
            adsData = False
            name, personaData, adsData  = ast.literal_eval(arg)
            if personaData == 'true':
                newsletter = True
            if adsData == 'true':
                adsData = True
            self.operationScenario.generateAccessCodeForPhone()
            self.operationScenario.attachPhoneNameAdwToCard(name, adsData)
            self.switchTo("PageInputAccessCode")

        if button == "personal_data_processing":
            self.switchTo("PageLicenseAccessText", text=self.operationScenario.getLicenseTextPersonalDataProcessing())

        if button == "adw_data_agreement":
            self.switchTo("PageLicenseAccessText", text=self.operationScenario.getLicenseTextAdwDataAgreement())

        if button == "main":
            self.operationScenario.disableAttachPhoneMode()
            self.operationScenario.clearTelephoneNumber()
            self.operationScenario.disablePageCardCloseRefuse()
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        # self.operationScenario.finishScenario()

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print "exit " + __name__
