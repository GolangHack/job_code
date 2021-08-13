# -*- coding: utf-8 -*-
from htmlpy_core.html_page import HtmlPage
import logging


class PageMain(HtmlPage):

    def onButtonClick(self, button, arg):
        robotEnabled = [self.operationScenario.isRobotAllowed(i) for i in range(self.robotCount)]
        robotMaintenance = [self.operationScenario.getRobotMaintenance(i) for i in
                            range(self.robotCount)]

        for i in range(self.robotCount):
            if button == 'robot' + str(i + 1):
                if self.operationScenario.getSmartSelection():
                    betterRobotIndex = self.operationScenario.getBetterRobotIndex()
                    if betterRobotIndex is not None:
                        selectedRobot = betterRobotIndex + 1
                        self.operationScenario.initRobot(selectedRobot)
                        self.switchTo('PageSelProgram')
                    else:
                        self.switchTo('PageWarningDeprecated',
                                      warning_text=u'В данный момент все роботы недоступны.')
                else:
                    if (not robotEnabled[i]) or (robotMaintenance[i] == 1):
                        self.switchTo('PageWarningDeprecated',
                                      warning_text=u'В данный момент этот робот недоступен.')
                        return
                    selectedRobot = i + 1
                    self.operationScenario.initRobot(selectedRobot)
                    if self.robotController[i].isRobotOccupied():
                        self.switchTo('PageWarningDeprecated',
                                      warning_text=u'Произведите оплату на терминале, '
                                                   u'когда Ваш автомобиль находится перед воротами...')
                    else:
                        self.switchTo('PageSelProgram')

        if button == 'client_card':
            print('Btn client card')
            self.switchTo('PageClientCard', card_price=self.operationScenario.getCardPrice())

        elif button == 'manual_mode':
            self.switchTo('PageInputSumManualMode')

    def onEnter(self, prevPage, *args, **kwargs):
        logging.getLogger(__name__).info("Enter page")
        print 'enter main page'
        self.maxCars = 1
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.finishScenario()
        self.robotCount = self.getVariable('robotsCount')
        self.robotController = self.getVariable('robotController')
        self.operationScenario.pay_qr_temporarily_not_work = False

    def onExit(self, nextPage, *args, **kwargs):
        logging.getLogger(__name__).info("Exit page")
        print 'exit main page'