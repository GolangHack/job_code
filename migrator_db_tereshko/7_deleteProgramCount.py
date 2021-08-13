#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
from data_storage.database import connection_manager
from data_storage.database import models_generated as db

import config
from uuid import uuid4 as uuid

PATH_TO_CONFIG_FILE = '../config.conf'


def getGroupByName(sectionname):
    """Получить группу по имени. Если ее нет, сгенерить и заретурнить, если есть, просто отдать ее"""
    try:
        return db.VariableGroup.get(db.VariableGroup.name == sectionname)
    except db.VariableGroup.DoesNotExist:
        vg = db.VariableGroup(id=uuid(), name=sectionname, description="Автоматически сгенерированная группа.")
        vg.save(force_insert=True)
        return vg

'Грузим настройки подключения к базе данных'

if config.readConfig(PATH_TO_CONFIG_FILE) is None:
    print u"config.conf не был найден. Создайте config.conf и настройки подключения к БД."
else:
    'Инициация подключения к БД'
    connection_manager.initConnection(config.getProperty('database_database'),
                                      host=config.getProperty('database_host'),
                                      password=config.getProperty('database_password'),
                                      user=config.getProperty('database_user'))
    db.database.execute_sql('delete from installation_has_variable  where variable_id in (SELECT id from variable where name like "ROBOT_%_%");')
    db.database.execute_sql('delete from notify_variable where variable_id in (SELECT id from variable where name like "ROBOT_%_%");')
    db.database.execute_sql('DELETE from variable where name like "ROBOT_%_%";')