#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by treeloys at 10.02.20

SQL если внезапно две копии программы

"""
import sys


sys.path.append('../')
from data_storage.database.models_generated import InstallationType, Installation
from data_storage.database import connection_manager

import config
from uuid import uuid4 as uuid

PATH_TO_CONFIG_FILE = '../config.conf'

'Грузим настройки подключения к базе данных'

if config.readConfig(PATH_TO_CONFIG_FILE) is None:
    print u"config.conf не был найден. Создайте config.conf и настройки подключения к БД."
else:
    'Инициация подключения к БД'
    connection_manager.initConnection(config.getProperty('database_database'),
                                      host=config.getProperty('database_host'),
                                      password=config.getProperty('database_password'),
                                      user=config.getProperty('database_user'))


    def createInstallation(number=0, name="Other", description="Прочее оборудование", allowed='1',
                           installation_type=None):
        return Installation.create(id=uuid(), number=number, name=name, description=description, allowed=allowed,
                                   installation_type=installation_type)


    def terminal(number=0, name="Terminal", description="Терминал", allowed='1'):
        return createInstallation(number=number, name=name, description=description, allowed=allowed,
                                  installation_type=InstallationType.get(InstallationType.name == "TERMINAL"))


    def robot(number=0, name="Robot", description="Робот", allowed='1'):
        return createInstallation(number=number, name=name, description=description, allowed=allowed,
                                  installation_type=InstallationType.get(InstallationType.name == "ROBOT"))

    # создаю робота с номером 2, обычно они идут 1, 2...
    robot(2)
if __name__ == "__main__":

    print u'Робот добавлен'

