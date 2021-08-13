# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging
from atol.atol import AtolCommandException

class PageSelBalance(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "show":
            self.switchTo("PageCardBalance")
        elif button == "print":
            lines = []
            lines.append(u'')
            lines.append(u'РоботКарВош')
            lines.append(u'')
            lines.append(u'Имя клиента: {}'.format(self.operationScenario.getClientName()))
            lines.append(u'')
            lines.append(u'Имя карты: {}'.format(self.operationScenario.getCardName()))
            lines.append(u'')
            lines.append(u'Номер клиентской карты: {}'.format(self.operationScenario.getCardUid()))
            lines.append(u'')
            lines.append(u'Баланс клиентской карты: {}'.format(self.operationScenario.getCardBalance()))
            lines.append(u'')
            if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                    self.operationScenario.vm.atolEnabled and
                    self.operationScenario.getHasPaper()):
                try:
                    self.kkm.printNonFiscalCheckMultiline(lines)
                except AtolCommandException as e:
                    logging.getLogger(__name__).error(u'{0}: {1}'.format(e.message, e.operationResult))
            self.switchTo("PageMain")
        elif button == "main":
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.kkm = self.getVariable('kkm')
        if not self.operationScenario.getHasPaper():
            self.setElementEnabled('print', False)

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
