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

    group_general = getGroupByName("InstallationStatistics")

    'Получить список роботов'
    robots = db.Installation.select().join(db.InstallationType).where(db.InstallationType.name == 'ROBOT')

    'Получить список программ'
    programs = (db.Program
                .select()
                .join(db.InstallationType)
                .switch(db.Program)
                .join(db.ProgramType)
                .where(db.InstallationType.name == 'ROBOT',
                       db.ProgramType.name == 'program')
                )

    'Создать переменные'
    for r in robots:
        for p in programs:
            var_id = uuid()
            forming_name = '_'.join(["ROBOT", str(r.number), "ProgramCount", "program", str(p.number)])
            db.Variable.create(id=var_id,
                               name=forming_name,
                               value="0",
                               default_value="0",
                               type="int",
                               description="Количество выполненных программ",
                               modifiable="1",
                               variable_group=group_general)
            db.InstallationHasVariable.create(id=uuid(),
                                              installation=r.id,
                                              variable=var_id)

        var_id = uuid()
        db.Variable.create(id=var_id,
                           name='_'.join(["ROBOT", str(r.number), 'ProgramCount', "LastUpdate"]),
                           value="",
                           default_value="",
                           type='',
                           description="Время последнего обновления счетчиков программ",
                           modifiable="1",
                           variable_group=group_general)

        db.InstallationHasVariable.create(id=uuid(),
                                          installation=r.id,
                                          variable=var_id)

        var_id = uuid()
        db.Variable.create(id=var_id,
                           name='_'.join(['ROBOT', str(r.number), 'ManualUsageCount']),
                           value="0",
                           default_value="0",
                           type='int',
                           description="Счетчик ручных запусков",
                           modifiable="1",
                           variable_group=group_general)

        db.InstallationHasVariable.create(id=uuid(),
                                          installation=r.id,
                                          variable=var_id)

        var_id = uuid()
        db.Variable.create(id=var_id,
                           name='_'.join(['ROBOT', str(r.number), 'WashesCount']),
                           value="0",
                           default_value="0",
                           type='int',
                           description="Количество запусков робота после сброса",
                           modifiable="1",
                           variable_group=group_general)

        db.InstallationHasVariable.create(id=uuid(),
                                          installation=r.id,
                                          variable=var_id)

        var_id = uuid()
        db.Variable.create(id=var_id,
                           name='_'.join(['ROBOT', str(r.number), 'WashesOffset']),
                           value="0",
                           default_value="0",
                           type='int',
                           description="Количество запусков робота до сброса",
                           modifiable="1",
                           variable_group=group_general)

        db.InstallationHasVariable.create(id=uuid(),
                                          installation=r.id,
                                          variable=var_id)
