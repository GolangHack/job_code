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

log = logging.getLogger(__name__)


class PageConfigEditor(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "saveChanges":
            data = json.loads(arg)
            for section in data:
                for param in data[section]:
                    config.setProperty(param, data[section][param])
        if button == "main":
            self.switchTo("PageMain")
        if button == "setPrevConfiguration":
            config.readConfig("config.conf")
            fileName = config.getProperty('config_name')
            backupFileName = fileName + ".back"
            config.readConfig(fileName)
            if os.path.isfile(backupFileName):
                with codecs.open(backupFileName, 'r', 'utf-8') as f:
                    with codecs.open(fileName, 'w', 'utf-8') as fw:
                        fw.write(f.read())
                log.info("Set prev config is success")
            else:
                log.info("Set prev config error. Not *.back file for configuration")
        if button == "setDefaultConfiguration":
            config.readConfig("config.conf")
            fileName = config.getProperty('config_name')
            defaultFileName = fileName + ".default"
            config.readConfig(fileName)
            if os.path.isfile(defaultFileName):
                with codecs.open(defaultFileName, 'r', 'utf-8') as f:
                    with codecs.open(fileName, 'w', 'utf-8') as fw:
                        fw.write(f.read())
                log.info("Set default config is success")
            else:
                log.info("Set default config error. Not *.default file for configuration")

    def preEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.finishScenario()
        allProperty = {}
        conf = config.getConfiguration()
        for section in conf.sections():
            allProperty[section] = {}
            for item in list(conf.items(section)):
                key, value = item
                if (type(value) == unicode):
                    allProperty[section][key] = value
                else:
                    allProperty[section][key] = str(value)
        self.setVariable(properties=allProperty, jsonproperty=json.dumps(allProperty))

    def onEnter(self, prevPage, *args, **kwargs):
        log.info("Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        log.info("Exit page")
        print "exit PageConfigEditor"
