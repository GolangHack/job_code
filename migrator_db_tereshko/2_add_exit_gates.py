#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by treeloys at 25.02.20
SQL если внезапно две копии программы
DELETE FROM variable WHERE `name` LIKE '%exit_gate%';

"""
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
    group_general = getGroupByName("general")
    db.Variable.create(id=uuid(),
                         name="cfg_exit_gate_open_output",
                         value="[6]",
                         default_value="[6]",
                         type="json",
                         description="",
                         modifiable="1",
                         variable_group=group_general)

    db.Variable.create(id=uuid(),
                         name="cfg_exit_gate_close_output",
                         value="[7]",
                         default_value="[7]",
                         type="json",
                         description="",
                         modifiable="1",
                         variable_group=group_general)

    db.Variable.create(id=uuid(),
                         name="cfg_exit_gates_emulate",
                         value="False",
                         default_value="False",
                         type="bool",
                         description="",
                         modifiable="1",
                         variable_group=group_general)

    db.Variable.create(id=uuid(),
                         name="cfg_exit_gates_disabled",
                         value="False",
                         default_value="False",
                         type="bool",
                         description="",
                         modifiable="1",
                         variable_group=group_general)

if __name__ == "__main__":
    print u'Миграция выполнена'
    print u'Необходимо переключить значения переменных для открытия врат'