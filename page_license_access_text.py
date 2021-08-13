# -*- coding: utf-8 -*-
import json
from pprint import pprint
import codecs
import os

import configparser

from htmlpy_core.html_page import HtmlPage
import logging


class PageLicenseAccessText(HtmlPage):
    def onButtonClick(self, button, arg):
        if button == "prev":
            # print arg
            print("arg:"+arg)
            self.switchTo("PageInputName")

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print "exit " + __name__
