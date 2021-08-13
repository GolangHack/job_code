# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging
from pyutils.delay import Delay


class PageNotCorrectPincode(HtmlPage):
    def onButtonClick(self, button, arg):
        pass

    def toInputPinCode(self):
        self.switchTo("PageInputAccessCode")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        Delay.once(5, self.toInputPinCode)

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
