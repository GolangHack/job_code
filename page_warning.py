# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging


class PageWarning(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == 'main':
            self.switchTo("PageMain")
        elif button == 'next':
            if self.nextPage == 'PageSelPay':
                self.switchTo('PageSelPay',
                              pay_description=self.operationScenario.generateDescription())
            else:
                self.switchTo(self.nextPage)

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self.nextPage = self.getVariable('next')
        logging.getLogger(__name__).info('Enter page')

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info('Exit page')
