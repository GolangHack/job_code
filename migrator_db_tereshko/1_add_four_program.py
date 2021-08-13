#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by treeloys at 10.02.20

SQL если внезапно две копии программы
DELETE FROM program_has_variable WHERE program_id = "1249332c-4a26-11ea-8c28-40490f504dd9";
DELETE FROM program_has_variable WHERE program_id = "1d1f1f36-4a25-11ea-8c28-40490f504dd9";
DELETE FROM variable WHERE `name` LIKE '%program_3%';
DELETE FROM program WHERE `name` LIKE '%Программа 4%';

"""
import sys
sys.path.append('../')
from data_storage.database import connection_manager
from data_storage.database.Installation import Robot
from data_storage.database.Program import CreateProgramPrice
import config

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
    # не выполнять два раза
    CreateProgramPrice(u"Программа 4",
                       3,
                       description=u'["Чистка рогов", "Чистка копыт", "Погладить"]',
                       prices={
                           "allowedNight": 1,
                           "default": 200,
                           "day": 200,
                           "night": 200,
                           "allowed": 200,
                           "HasOptions": True
                       },
                       installation_type=Robot).create()

if __name__ == "__main__":
    print u'Миграция выполнена'

