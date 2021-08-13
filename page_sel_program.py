# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging
from calendarEvents import CalendarEvents

class PageSelProgram(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "main":
            self.switchTo("PageMain")
        else:
            pnumber = int(button.split("_")[1])
            program = self.utilityManager.getUtility('program', pnumber)
            self.operationScenario.setProgramNumber(pnumber)
            self.operationScenario.setProgramName(program.getCaption())
            self.operationScenario.setProgramPrice(program.getPrice())
            if not self.operationScenario.getDryZoneDisabled() and program.hasOptions():
                self.switchTo("PageSelService")
            else:
                self.washingPrice = self.operationScenario.getProgramPrice()
                self.operationScenario.setSpendingSum(self.washingPrice)
                self.operationScenario.setServicesMask(0)
                self.switchTo("PageSelPay",
                              pay_description=self.operationScenario.generateDescription())

    def preEnter(self, prevPage, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.lockQrReader(self.operationScenario.getRobotNumber() - 1)
        self.utilityManager = self.getVariable('utilityManager')

        self.program = []
        self.night_price = []
        for p in self.utilityManager.getUtilities('program'):
            self.program.append(u'{} {}₽'.format(p.getCaption(), p.getPrice()))
            self.night_price.append(u'{}'.format(p.getNightPrice()))

        self.setVariable(program=self.program)
        self.setVariable(night_price=self.night_price)

        for p in self.utilityManager.getUtilities('program'):
            self.setElementEnabled('prg_{}'.format(p.getIndex()), p.isEnabled())

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print "exit program page"
