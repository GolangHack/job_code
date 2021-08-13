# -*- coding: utf-8 -*-
import logging

from htmlpy_core.html_page import HtmlPage
from page_sel_pay import PageSelPay
from page_sel_service import PageSelService
from page_card_close import PageCardClose
from operation_scenario import OperationScenario


class PageWarningContinue(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "next":
            if isinstance(self._prevPage, PageSelService):
                self.switchTo("PageSelPay")
            if isinstance(self._prevPage, PageSelPay):
                self.switchTo("PagePayCash")
            if isinstance(self._prevPage, PageCardClose):
                cardClosePurpose = self.operationScenario.getCardClosePurpose()
                if cardClosePurpose == OperationScenario.CARD_CLOSE_PURPOSE_FILL_CARD:
                    self.switchTo("PageSelPay")
                elif cardClosePurpose == OperationScenario.CARD_CLOSE_PURPOSE_SHOW_BALANCE:
                    self.switchTo("PageSelBalance")
        elif button == "main":
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        self.operationScenario = self.getVariable('operationScenario')
        self._prevPage = prevPage
        logging.getLogger(__name__).info("Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
