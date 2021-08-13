# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging
import pyutils


class PageErrorPhoneIsBinded(HtmlPage):
    def onButtonClick(self, button, arg):
        pass

    def toPageInputPhone(self):
        self.switchTo("PageInputPhone")

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        pyutils.delay.Delay.once(5, self.toPageInputPhone)

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
