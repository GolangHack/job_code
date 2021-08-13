# -*- coding: utf-8 -*-
import logging

from atol.atol import AtolCommandException
from htmlpy_core.html_page import HtmlPage

from pyutils.delay import Delay

log = logging.getLogger(__name__)


class PageWarningClearReportsBuffer(HtmlPage):

    def onButtonClick(self, button, arg):
        print("BUTTON ", button, " PRESSED")
        if button == "main":
            self.switchTo("PageMain")

        elif button == "print":
            log.info("GUI Printing z report from buffer")
            self.operationScenario.vm.printBufferZandXReport()
            self.switchTo("PageMain")

        elif button == "clear":
            log.info("GUI Clear z report buffer")
            self.operationScenario.vm.clearBufferZandXReport()
            self.switchTo("PageMain")

        elif button == "createReport":
            log.info("GUI Create report buffer")
            try:
                self.operationScenario.vm.createZReportInBuffer()
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))
                if e.operationResult.code == -3828:
                    self.showErrorModal(u'Не удалось создать Z-отчет, смена уже закрыта.')

    def onEnter(self, prevPage, *args, **kwargs):
        log.info(" Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.delay = Delay.periodic(1, self.updateReportsCount)

    def onExit(self, nextPage, *args, **kwargs):
        log.info(" Exit page")
        if self.delay is not None:
            self.delay.cancel()

    def showErrorModal(self, msg):
        self._back_end.evaluateJS("document.getElementById('btn-on').style.visibility = 'hidden';")
        self._back_end.evaluateJS(u"showModal('modal','<h4>Внимание</h4><p>{}</p>');".format(msg))

    def updateReportsCount(self):
        count = 0
        try:
            count = self.operationScenario.vm.getReportsCountFromBuffer()
        except AtolCommandException as e:
            log.error(u'{0}: {1}'.format(e.message, e.operationResult))
        finally:
            self.changeValueById('reports_count', value=count)
            self.setElementEnabled('print', enabled=(count != 0))
            self.setElementEnabled('clear', enabled=(count != 0))
