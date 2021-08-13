# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from operation_scenario import OperationScenario
import logging

class PageErrorBillAcceptor(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "exit-btn":
            self.exitCounter += 1
        if self.exitCounter == 3:
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.exitCounter = 0
        self.operationScenario = self.getVariable('operationScenario')
        inserted = self.operationScenario.getMoneyInserted()
        error, dispensed, not_dispensed = self.operationScenario.getBillDispenseResult()
        if error is True:
            self.setVariable(error_name=u'Ошибка купюроразменника')
            self.changeValueById('inserted', u'Внесено денег: {}р.'.format(inserted))
            self.changeValueById('dispensed', u'Количество выданных купюр: {}'.format(dispensed))
            self.changeValueById('not-dispensed',
                                 u'Количество задержанных купюр: {}'.format(not_dispensed))
        else:
            self.setVariable(error_name=u'Ошибка купюроприемника')
            self.changeValueById('inserted', u'Внесено денег: {}р.'.format(inserted))

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
