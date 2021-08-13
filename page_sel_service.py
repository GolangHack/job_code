# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
from threading import Timer
from operation_scenario import OperationScenario
import logging
from calendarEvents import CalendarEvents

class PageSelService(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "next":
            self.operationScenario.setServiceSelected(self.servicesPay)
            if self.operationScenario.atolModeOnlyQrCodeCheck():
                self.switchTo("PageSelPay", pay_description=self.operationScenario.generateDescription())
            elif not self.operationScenario.atolModeOnlyQrCodeCheck() and self.operationScenario.vm.fiskal_check_disabled:
                if self.operationScenario.getHasPaper():
                    self.switchTo("PageSelPay", pay_description=self.operationScenario.generateDescription())
                else:
                    self.switchTo("PageWarning", next="PageSelPay",
                                  warning_text=u'В данный момент терминал не выдаёт бумажные чеки.<br>'
                                               u'Хотите продолжить?')
            else:
                if self.operationScenario.getHasPaper():
                    self.switchTo("PageSelPay", pay_description=self.operationScenario.generateDescription())
                else:
                    self.switchTo("PageWarning", next="PageSelPay",
                                  warning_text=u'В данный момент терминал не выдаёт бумажные чеки.<br>'
                                               u'Хотите продолжить?')
        elif button == "main":
            self.switchTo("PageMain")
        else:
            index = int(button.split("_")[1])
            self.services[index] = not self.services[index]
            if self.services[index]:
                self.operationScenario.setSpendingSum(self.operationScenario.getSpendingSum() + self.utilityManager.getUtility('service', index).getPrice())
                self.operationScenario.setServicesMask(self.operationScenario.getServicesMask() | (1 << index))
                self.servicesPay[index] = self.utilityManager.getUtility('service', index).getPrice()
            else:
                self.operationScenario.setSpendingSum(self.operationScenario.getSpendingSum() - self.utilityManager.getUtility('service', index).getPrice())
                self.operationScenario.setServicesMask(self.operationScenario.getServicesMask() & (~(1 << index)))
                self.servicesPay[index] = 0
            self.setOptionChecked(button, self.services[index])


    def setOptionChecked(self, id, val):
        if val:
            self.addClassById(id, "checked")
        else:
            self.removeClassById(id, "checked")

    def preEnter(self, prevPage, *args, **kwargs):
        self.servicesPay = []
        self.service = []
        self.utilityManager = self.getVariable('utilityManager')
        self.operationScenario = self.getVariable('operationScenario')

        self.washingPrice = self.operationScenario.getProgramPrice()
        self.operationScenario.setSpendingSum(self.washingPrice)
        self.operationScenario.setServicesMask(0)
        self.timeOfDay = self.operationScenario.getTimeOfDay()

        # if self.utilityManager.getNightDisabled('service') and self.timeOfDay == CalendarEvents.NIGHT:
        if self.utilityManager.isDisabledAtNight('service'):
            self.setVariable(service_title = u'Дополнительные опции доступны днем')
        else:
            self.setVariable(service_title = u'Выберите дополнительные опции')


        logging.getLogger(__name__).info("Spending sum: {}".format(self.operationScenario.getSpendingSum()))
        self.services = [False] * 6
        self.servicesPay = [0] * 6

        for s in self.utilityManager.getUtilities('service'):
            self.service.append(u'{} {}{}'.format(s.getCaption(), s.getPrice(), u'₽'))

        self.setVariable(service = self.service)

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        for s in self.utilityManager.getUtilities('service'):
            self.setElementEnabled('opt_{}'.format(s.getIndex()), s.isEnabled())
        if (self.operationScenario.vm.services_unavailability_for_individual_robots_enable
                and self.operationScenario.getTimeOfDay() == 'night'):
            if self.operationScenario.vm.availability_robotic_services[self.operationScenario.getRobotNumber()-1] == 0:
                for s in self.utilityManager.getUtilities('service'):
                    self.setElementEnabled('opt_{}'.format(s.getIndex()), False)
                for r in range(self.operationScenario.vm.robots_count):
                    if self.operationScenario.vm.availability_robotic_services[r-1] == 1:
                        self.setVariable(service_title=u'Дополнительные опции доступны на другом роботе')
        if not self.operationScenario.atolModeOnlyQrCodeCheck():
            self.operationScenario.setHasPaper(self.operationScenario.checkHasPaper())

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
