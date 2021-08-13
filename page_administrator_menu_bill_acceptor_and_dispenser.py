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
from pyutils.delay import Delay


class PageAdministartorMenuBillAcceptorAndDispenser(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")

        if button == "clearTopFloat":
            self.operationScenario.billDispenserClearTopFloat()

        if button == "refreshDispenserStatus":
            self.operationScenario.refreshBillDispenserStatus()
            self.changeValueById('message', u'Статус обновлен.')

        if button == "inhibitOff":
            self.changeButtonsState(
                isBtnInhibitOffEnabled=False,
                isBtnInhibitOnEnabled=True,
                isBtnClearTopFloatEnabled=True)
            self.operationScenario.vm.enableMoneyReceive()

        if button == "inhibitOn":
            self.changeButtonsState(
                isBtnInhibitOnEnabled=False,
                isBtnInhibitOffEnabled=True,
                isBtnClearTopFloatEnabled=False)
            self.operationScenario.vm.disableMoneyReceive()

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        def _onBillsPositionResult():
            res = self.operationScenario.vm.getAvailableChangeBills()
            self.changeValueById("counterBills",
                                 res)

        self.d = Delay.periodic(2, _onBillsPositionResult)
        self.changeButtonsState(
            isBtnInhibitOnEnabled=False,
            isBtnInhibitOffEnabled=True,
            isBtnClearTopFloatEnabled=False)
        # TODO
        self.setVariable(billAcceptorTypename=self.operationScenario.vm.billAcceptorTypename)

    def onExit(self, nextPage, *args, **kwargs):
        if self.d:
            self.d.cancel()
        self.operationScenario.vm.disableMoneyReceive()
        logging.getLogger(__name__).info("Exit page")
        print "exit " + __name__

    def changeButtonsState(self, isBtnInhibitOnEnabled,
                           isBtnInhibitOffEnabled, isBtnClearTopFloatEnabled):
        self.setElementEnabled('inhibitOn', enabled=isBtnInhibitOnEnabled)
        self.setElementEnabled('inhibitOff', enabled=isBtnInhibitOffEnabled)
        self.setElementEnabled('clearTopFloat', enabled=isBtnClearTopFloatEnabled)
