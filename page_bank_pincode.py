# -*- coding: utf-8 -*-
import logging

from htmlpy_core.html_page import HtmlPage


class PageBankPincode(HtmlPage):

    def __init__(self, *args, **kwargs):
        super(PageBankPincode, self).__init__(*args, **kwargs)
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.registerUpdatePincodeMaskHandler(self.updatePincodeMask)

    def onEnter(self, prevPage, *args, **kwargs):
        logging.info(__name__ + " Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        logging.info(__name__ + " Exit page")

    def updatePincodeMask(self, pincodeMask):
        if len(pincodeMask) == 1:
            pincodeMask = '* _ _ _'
        elif len(pincodeMask) == 2:
            pincodeMask = '* * _ _'
        elif len(pincodeMask) == 3:
            pincodeMask = '* * * _'
        elif len(pincodeMask) == 4:
            pincodeMask = '* * * *'
        else:
            pincodeMask = '_ _ _ _'
        self.changeValueById('pincodeMask', pincodeMask)
