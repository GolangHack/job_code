# -*- coding: utf-8 -*-
import threading
import time

from htmlpy_core.html_page import HtmlPage
#from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging

log = logging.getLogger(__name__)


class PageWantPrint(HtmlPage):#создаем класс

    def onButtonClick(self, button, arg):#создаем функцию
        if button == "print":#кнопка 
            self.operationScenario.setWantPrintCheck(True)#напечатать чек
            self.switchTo("PageCheckPrinting")#выполняем переброс к PageCheckPrinting
        elif button == "skip":#button skip
            log.info("Refuse printing")#попытка перезапустить принтинг
            self.operationScenario.setWantPrintCheck(False)#вывод суммы без чека
            print("Payment without printing check")
            self.operationScenario.pay()#оплата
            if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                self.switchTo("PageQueueNumber")#номер в очереди
            else:
                self.switchTo("PageQRCode")#отправиться к странице очереди

    def onEnter(self, prevPage, *args, **kwargs):
        log.info("Enter page")#страница входа
        "Если режим только qr чеки, то даже не спраивать"
        self.operationScenario = self.getVariable('operationScenario')

    def onExit(self, nextPage, *args, **kwargs):
        log.info("Exit page")#страница выхода
