# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
#from threading import Timer
from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging

class PageBillDispenserFailed(HtmlPage):

    def onButtonClick(self, button, arg):#функция нажатия кнопки 

        if button == "next":#если нажата переходим на PsgePayCash
            self.switchTo("PagePayCash")

        elif button == "main":#если нажата переходим на PageMain
            self.switchTo("PageMain")

    def onEnter(self, prevPage, *args, **kwargs):

        self.operationScenario = self.getVariable('operationScenario')
        if self.operationScenario.atolModeOnlyQrCodeCheck():#если сработала qrcheck
            self.changeElementVisibility(id='paper_is_out', visible=False)#изменить видимость

        else:
            isPaperOut = not self.operationScenario.checkHasPaper()#если бумага не выдана
            self.operationScenario.setHasPaper(not isPaperOut)
            self.changeElementVisibility(id='paper_is_out', visible=isPaperOut)#изменить видимость элемента
        logging.getLogger(__name__).info("Enter page")

    def onExit(self, nextPage, *args, **kwargs):
        # self.operationScenario.pay()
        logging.getLogger(__name__).info("Exit page")#выход
