#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
from htmlpy_core.html_page import HtmlPage
from pyutils.delay import Delay


class PageOperatorMenu(HtmlPage):

    def onButtonClick(self, button, arg):
        def swap(val): return (1, 0)[val]

        for i, robot in enumerate(self.robotController, 1):
            if button == 'reset_car_in_robot_{}'.format(i):
                robot.finishWashing()
                robot.resetCarPosition()
                print 'reset_car_in_robot_{}', i
            if button == 'open_entry_gate_{}'.format(i):
                print 'open_entry_gate_', i
                robot.openEntryGate()
            if button == 'close_entry_gate_{}'.format(i):
                robot.closeEntryGate()
                print 'close_entry_gate_', i
            if button == 'open_exit_gate_{}'.format(i):
                robot.openExitGate()
                print 'open_exit_gate_', i
            if button == 'set_robot_maintenance_{}'.format(i):
                mode = self.operationScenario.getRobotMaintenance(i - 1)
                self.setRobotMaintenance((i - 1), swap(mode))
                print 'set_robot_maintenance_', i

        if button == 'main':
            self.switchTo('PageMain')

        if button == 'reboot':
            os.system('sudo reboot')

    def onEnter(self, previousPage, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.log.info("Enter page")
        self.robotsCount = self.getVariable('robotsCount')
        self.robotController = self.getVariable('robotController')
        self.operationScenario = self.getVariable('operationScenario')
        self.initialRobotMaintenance()
        self.delay = Delay.periodic(1, self.updateScreen)

    def onExit(self, targetPage, *args, **kwargs):
        self.log.info("Exit page")
        if self.delay is not None:
            self.delay.cancel()

    def updateScreen(self):
        self.updateSensors()
        self.updateCarPosition()
        self.updateRobotConnection()
        self.updateRobotState()

    def updateSensors(self):
        """
        Обновляет цвет датчиков положения автомобиля, если датчик перекрыт,
        то цвет датчика на экране меняется на красный, если нет - на зеленый
        """
        for i, robot in enumerate(self.robotController, 1):
            state = robot.getLastSensorsState()
            sensors = {'ent_sensor_state_{}'.format(i): state[0],
                       'mid_sensor_state_{}'.format(i): state[1],
                       'ext_sensor_state_{}'.format(i): state[2]}
            for id, state in sensors.items():
                if state is False:
                    self.changeClassById(id, _from='green', _to='red')
                else:
                    self.changeClassById(id, _from='red', _to='green')

    def updateCarPosition(self):
        """
        Обновляет состояние наличия машины внутри, если машина внутри, то
        на экране отображается изображение машины с кнопка 'Сбросить', если
        машины внутри нет, то кнопка 'Сбросить' и изображение машины не видны
        на экране.
        """
        for i, r in enumerate(self.robotController, 1):
            id = 'car_{}'.format(i)
            if (r.getCarPosition() == 'no') or (r.getYellowZoneLength() == 0):
                self.changeClassById(id, _from='car', _to='no-car')
            else:
                self.changeClassById(id, _from='no-car', _to='car')

    def updateRobotConnection(self):
        """
        Обновляет цвет блока с надписью робот, если робот недоступен,
        надпись становится красной
        """
        for i, robot in enumerate(self.robotController, 1):
            id = 'robot_{}_status'.format(i)
            if robot.isConnected():
                self.changeClassById(id, _from='disconnected', _to='connected')
            else:
                self.changeClassById(id, _from='connected', _to='disconnected')

    def updateRobotState(self):
        """
        Обновляет блок с роботом, если робот находится в ошибке, то блок
        с надписью 'Робот N' становится красным, если робот не находится
        в ошибке, цвет блока остается неизменным.
        """
        for i, robot in enumerate(self.robotController, 1):
            id = 'robot_{}'.format(i)
            if robot.inErrorState():
                self.addClassById(id, 'red')
            else:
                self.removeClassById(id, 'red')

    def initialRobotMaintenance(self):
        """
        Устанавливает текст кнопки: робот включен / выключен при загрузке страницы.
        """
        for robot in range(self.robotsCount):
            mode = self.operationScenario.getRobotMaintenance(robot)
            self.setRobotMaintenance(robot, mode)

    def setRobotMaintenance(self, robot, mode):
        """
        Обновляет текст кнопки, устанавливающей: робот включен / выключен.
        """
        id = 'robot_{}_maintenance'.format(robot + 1)
        self.changeValueById(id, u'Выключен' if (mode == 1) else u'Включен')
        self.operationScenario.setRobotMaintenance(robot, mode)
