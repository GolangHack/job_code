# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging


class PageSleepMode(HtmlPage):

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info('Enter page')
        print ('Enter PageSleepMode')

    def onButtonClick(self, button, arg):
        if button == "enterMainPage":
            self.switchTo("PageMain")

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info('Exit page')
        print ('Exit PageSleepMode')
