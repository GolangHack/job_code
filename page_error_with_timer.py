# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging
import pyutils


class PageErrorWithTimer(HtmlPage):
    def onButtonClick(self, button, arg):
        pass

    def toPageInputPhone(self):
        print "exit page error with timer page"
        self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):
        print "enter page error with timer page"
        logging.getLogger(__name__).info("Enter page")
        delayTime = self.getVariable("delay_time")
        pyutils.delay.Delay.once(delayTime, self.toPageInputPhone)

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
