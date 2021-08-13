#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт автоматического сохранения данных из таблицы
finance, формирование csv отчета и отправка на email.
вызывается рас в день
"""
import sys

sys.path.append("..")
import datetime
import json
import csv
import time
from jinja2 import Environment, PackageLoader, select_autoescape
# удалить нахер
import config
import logging
import pdfkit
from email_notifier import EmailNotifier
import data_storage.database.connection_manager as connection_manager
import data_storage.database.models_generated as db
import data_storage.database.settingsManager as sm
# Загрузка параметров из конфигов
PATH_TO_CONFIG_FILE = '../config.conf'

if config.readConfig(PATH_TO_CONFIG_FILE) is None:
    print u"{} не был найден. Создайте config.conf и настройки подключения к БД.".format(PATH_TO_CONFIG_FILE)
else:
    'Инициация подключения к БД'
    connection_manager.initConnection(config.getProperty('database_database'),
                                      host=config.getProperty('database_host'),
                                      password=config.getProperty('database_password'),
                                      user=config.getProperty('database_user'))
    config.readConfigFromCurrentDB()


    # Настройка логгеров
    logfile_path_remote = config.getProperty("logfile_path_remote")
    logging.basicConfig()
    log = logging.getLogger("general")
    log.setLevel(logging.INFO)
    fh = logging.FileHandler("../" + logfile_path_remote + "scheduler.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)

#
# def excepthook(excType, excValue, traceback):
#     log.error("Error:",
#               exc_info=(excType, excValue, traceback))
#
#
# sys.excepthook = excepthook

log.info("*****START SCHEDULER******")
#############

# подключения к БД
database_host = config.getProperty('database_host')
database_user = config.getProperty('database_user')
database_password = config.getProperty('database_password')
database_database = config.getProperty('database_database')

# настройки csv
csv_path = "temp.csv"
csv_path_all = "allTemp.csv"
csv_delimiter = ";"

# настройки email
sender = config.getProperty('email_sender')
pwd = config.getProperty('email_pwd')
receivers = json.loads(config.getProperty('email_receivers'))
serv = config.getProperty('email_server')
emailNotifier = EmailNotifier(sender, receivers, serv, sender, pwd)

# настройки формирования отчета

robots_count = int(config.getProperty('robots_count'))
# TODO переделать, взять из таблиц
service_name = json.loads(config.getProperty('service_name').replace("<br>", " "))
report_name_wash = config.getProperty('report_name_wash', default="Внимание! Не найдено имя мойки.")
report_all_time_start = config.getProperty('report_all_time_start', default="2019-04-1")
report_all_datetime_start = datetime.datetime.strptime(report_all_time_start, "%Y-%m-%d")
report_hour, report_minutes = config.getProperty('report_time', '9:00').split(":")
report_hour = int(report_hour)
report_minutes = int(report_minutes)
###############
# вспомогательные методы

def filters_unpack_for_wash(unpackList):
    """
    :type unpackList: только простые значения для заполнения
    """
    return ",".join(str(x) for x in unpackList)


def filters_upack_key(unpackList):
    return [str(x + 1) for x in range(len(unpackList) - 1)]


def filters_unpack_for_wash_dict(unpackListAttachDict):
    """
    :type unpackListAttachDict: распаковка с содержанием словаря
    """
    # инициация списка хранения, где ключ - это число, а значение, возможные значения роботов для заполнения
    unpacked = {}
    for key in unpackListAttachDict[-1].keys():
        unpacked[key] = []

    for id_robot, values in enumerate(unpackListAttachDict):
        for key in unpackListAttachDict[-1].keys():
            if key in values:
                unpacked[key].append(values[key])
            else:
                unpacked[key].append(0)
    return unpacked


def jinja_process(datetime_start, datetime_end, template_filename='oneDayForCsv.jinja2'):
    """
    :type finance: Выгрузка из базы в виде словаря
    """
    # jinja2 инициация
    env = Environment(
        loader=PackageLoader(__name__, 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    env.filters['unpack_for_wash'] = filters_unpack_for_wash
    env.filters['unpack_for_wash_dict'] = filters_unpack_for_wash_dict
    env.filters['unpack_key'] = filters_upack_key
    template = env.get_template(template_filename)
    dtr = datetime.datetime.now()
    dtr = dtr.replace(hour=report_hour, minute=report_minutes)
    template.globals['now'] = dtr.strftime("%d.%m.%Y %H:%M")
    template.globals['nowinterwal'] = (dtr - datetime.timedelta(days=1)).strftime(
        "%d.%m.%Y %H:%M")
    dtrs = datetime.datetime.strptime(report_all_time_start, '%Y-%m-%d')
    template.globals['report_all_time_start'] = dtrs.strftime("%d.%m.%Y %H:%M")
    # подсчет количества нужных полей
    data = {
        ##############
        # Общая информация
        # куплено карт
        "bought_cards": 0,
        # количество купюр выданных на здачу
        "take_bils_on_shor_change": 0,
        # Количество моек по программе
        "wash_on_programs_name": {},
        "wash_on_programs_count": {},
        # Все вместе, и столбец "итог"
        "program_archive": {},
        # Количество оплат клиентскими картами
        "payment_by_client_cards": 0,
        ###############
        # Финансовая информация. Мойки. Инициация количество роботов + 1 для итогов
        # Внесенных средств
        "inserted_money": [0] * (robots_count + 1),
        # Внесенных наличных средств
        "insert_nal_money": [0] * (robots_count + 1),
        # Внесенных с клиентских карт средств
        "insert_client_card_money": [0] * (robots_count + 1),
        # Внесенных с банковских карт средств
        "insert_bank_card_money": [0] * (robots_count + 1),
        # Сумма оплат за программу
        "payment_by_programs": [{} for x in range(robots_count + 1)],
        # Сумма оплат за опцию
        "payment_by_services": [{} for x in range(robots_count + 1)],
        "all_payment_info_by_program": [],
        ################
        # Финансовая информация. Клиентские карты
        # Внесенных средств
        "card_inserted_money": 0,
        # Внесенных наличных средств
        "card_insert_nal_money": 0,
        # Внесенных с банковских карт средств
        "card_insert_bank_card_money": 0,
        # Сумма оплат за приобретение клиентской карты
        "card_sum_bought_cards": 0,
        # Сумма кэшбэка, перечисленного на клиентские карты
        "card_sum_cashback_send_cards": 0
    }
    sql_between_datetime_select = "(finance.`date_time` BETWEEN '{0}' AND '{1}')".\
        format(datetime_start.strftime("%Y-%m-%d %H:%M:%S"), datetime_end.strftime("%Y-%m-%d %H:%M:%S"))

    # куплено карт
    cursor = db.database.execute_sql("""
        SELECT COUNT(*)
        FROM finance
        WHERE 
        (finance.pay_destination_type_id = 0) AND
        (%s);""" % sql_between_datetime_select)
    data["bought_cards"] = cursor.fetchone()[0]

    # количество купюр выданных на здачу
    cursor = db.database.execute_sql("""
        SELECT SUM(bills_dispensed.amount)
        FROM bills_dispensed, finance
        WHERE bills_dispensed.finance_id = finance.id AND
        (%s);""" % sql_between_datetime_select)
    data["take_bils_on_shor_change"] = cursor.fetchone()[0]

    # Количество оплат клиентскими картами
    cursor = db.database.execute_sql("""
        SELECT COUNT(*)
        FROM  finance
        WHERE
        (finance.pay_source_type_id = 2) AND
        (finance.pay_destination_type_id = 2) AND
            (%s);""" % sql_between_datetime_select)
    data["payment_by_client_cards"] = cursor.fetchone()[0]
    ###########################
    # финансовая информация
    'Запрос на выборку роботов'
    cursor = db.database.execute_sql("""
            SELECT installation.id, installation.number
            FROM installation, installation_type
            WHERE installation.installation_type_id = installation_type.id AND installation_type.id=3
            GROUP BY installation.id
            order by installation.number;
                        """)
    column_sql_select_on_robot_1 = ""
    column_sql_select_on_robot_2 = ""
    for row in cursor.fetchall():
        column_sql_select_on_robot_1 += \
            "SUM(IF(finance.dest_installation_id = '{0}', finance_price_archive.price, 0)) AS `Робот {1}`, ".format(row[0], row[1])
        column_sql_select_on_robot_2 += \
            "SUM(IF(finance.dest_installation_id = '{0}', finance.amount, 0)) AS `Робот {1}`, ".format(row[0], row[1])

    # Внесенных средств
    cursor = db.database.execute_sql("""
        SELECT {0} SUM(amount)
        FROM  finance
        WHERE
        (finance.pay_destination_type_id = 2) AND
            ({1});""".format(column_sql_select_on_robot_2, sql_between_datetime_select))
    data["inserted_money"] = cursor.fetchone()

    # Внесенных наличных средств
    cursor = db.database.execute_sql("""
        SELECT {0} SUM(amount) 
        FROM finance
        WHERE
        /*Кэш*/
        (finance.pay_source_type_id = 1) AND
        /*Оплата работы мойки*/
        (finance.pay_destination_type_id = 2) AND
                ({1});""".format(column_sql_select_on_robot_2, sql_between_datetime_select))
    data["insert_nal_money"] = cursor.fetchone()

    # Внесенных с клиентских карт средств
    cursor = db.database.execute_sql("""
        SELECT {0} SUM(amount) 
        FROM finance
        WHERE
        /*Кэш*/
        (finance.pay_source_type_id = 2) AND
        /*Оплата работы мойки*/
        (finance.pay_destination_type_id = 2) AND
                ({1});""".format(column_sql_select_on_robot_2, sql_between_datetime_select))
    data["insert_client_card_money"] = cursor.fetchone()

    # Внесенных с банковских карт средств
    cursor = db.database.execute_sql("""
        SELECT {0} SUM(amount) 
        FROM finance
        WHERE
        /*Кэш*/
        (finance.pay_source_type_id = 0) AND
        /*Оплата работы мойки*/
        (finance.pay_destination_type_id = 2) AND
                ({1});""".format(column_sql_select_on_robot_2, sql_between_datetime_select))
    data["insert_bank_card_money"] = cursor.fetchone()
    # ************************************
    # Cумма оплат за программу

    cursor = db.database.execute_sql("""
            SELECT
                CONCAT('Сумма оплат за ', finance_price_archive.program_name) AS `Наименование`,
                {0}
                SUM(finance_price_archive.price) AS `Итог`
            FROM finance_price_archive, finance
            WHERE finance_price_archive.finance_id = finance.id
            AND ({1})
            GROUP BY finance_price_archive.program_name ORDER BY finance_price_archive.program_type_name;
            """.format(column_sql_select_on_robot_1, sql_between_datetime_select))

    for row in cursor.fetchall():
        data["all_payment_info_by_program"].append(row)
    #####################################
    # Клиентские карты

    # Внесенных средств
    cursor = db.database.execute_sql("""
        SELECT SUM(amount) 
        FROM finance
        WHERE
        (finance.pay_destination_type_id = 1) AND
                (%s);""" % sql_between_datetime_select)
    data["card_inserted_money"] = cursor.fetchone()[0]

    # Внесенных наличных средств
    cursor = db.database.execute_sql("""
        SELECT SUM(amount) FROM  finance
        WHERE
        /*Кэш*/
        (finance.pay_source_type_id = 1) AND
        /*Оплата работы мойки*/
        (finance.pay_destination_type_id = 1) AND
                        (%s);""" % sql_between_datetime_select)
    data["card_insert_nal_money"] = cursor.fetchone()[0]

    # Внесенных с банковских карт средств
    cursor = db.database.execute_sql("""
            SELECT SUM(amount) FROM  finance
            WHERE
            /*Кэш*/
            (finance.pay_source_type_id = 0) AND
            /*Оплата работы мойки*/
            (finance.pay_destination_type_id = 1) AND
                            (%s);""" % sql_between_datetime_select)
    data["card_insert_bank_card_money"] = cursor.fetchone()[0]

    # Сумма оплат за приобретение клиентской карты
    cursor = db.database.execute_sql("""
        SELECT sum(amount)
        FROM finance
        WHERE 
        (finance.pay_destination_type_id = 0) AND
            (%s);""" % sql_between_datetime_select)
    data["card_sum_bought_cards"] = cursor.fetchone()[0]

    # Сумма кэшбэка, перечисленного на клиентские карты
    cursor = db.database.execute_sql("""
        SELECT sum(finance.cashback_amount)
        FROM finance
        WHERE 
        (finance.pay_destination_type_id = 1) AND
            (%s);""" % sql_between_datetime_select)
    data["card_sum_cashback_send_cards"] = cursor.fetchone()[0]
    # приведение списков к удобоваримой форме для шаблонизатора
    data["payment_by_services"] = filters_unpack_for_wash_dict(data["payment_by_services"])
    data["payment_by_programs"] = filters_unpack_for_wash_dict(data["payment_by_programs"])
    # Сервисы
    data["service_name"] = service_name
    preRegexDataForCsv = template.render(data=data)
    # убираем лишние новые строки(не опечтка, две строки должны быть)
    preRegexDataForCsv = preRegexDataForCsv.replace("\n\n", "\n")
    preRegexDataForCsv = preRegexDataForCsv.replace("\n\n", "\n")
    return preRegexDataForCsv


class Report(object):
    PATH_TO_TEMP = "./temp/"

    def __init__(self, name="temp", format_document=None, data=None):
        """
        Генерирует рапорты
        :param format_document: только два значения 'csv' и 'pdf'
        :param data: дата в соответствии с типом данных
        :param name: Имя файла в сообщении
        """
        self.format = ''
        self.file_for_send = ""
        self.file_name_in_temp_folder = name + "."
        if format_document and data:
            if format_document == "csv":
                self.create_cvs(data)
            if format_document == "pdf":
                self.create_pdf(data)

    def set_filename(self, name):
        self.file_name_in_temp_folder = name

    def get_path_to_generied(self):
        return self.file_for_send

    def _generate_path_to_tempfile(self, format):
        self.format = format
        self.file_for_send = self.PATH_TO_TEMP + self.file_name_in_temp_folder + "." + format
        return self.file_for_send

    def create_cvs(self, csv_data):
        file_report = self._generate_path_to_tempfile("csv")
        with open(file_report, "w") as csv_file:
            csv_file.write(csv_data.encode("utf-8"))
        log.info(u"Сформирован отчет csv: \n" + unicode(csv_data))

    def create_pdf(self, html_data):
        file_report = self._generate_path_to_tempfile("pdf")
        pdfkit.from_string(html_data, file_report)

        log.info(u"Сформирован отчет pdf: \n" + unicode(html_data))

    def send(self, msg, attach_filename="report"):
        emailNotifier.notifyFile(self.file_for_send,
                                 msg,
                                 "%s %s.%s" % (attach_filename,
                                               str(time.asctime()),
                                               self.format
                                               ))
        log.info(u"Сообщение общий отправлено")
        log.info(u"**************************")


class Reports(object):
    def __init__(self):
        self.reports = []

    def add_report(self, report):
        report.set_filename(str(len(self.reports)) + "temp")
        self.reports.append(report)

    def send(self, msg, theme=None):
        paths = []
        for report in self.reports:
            paths.append(report.file_for_send)
        if theme:
            emailNotifier.notifyFiles(paths, msg, theme)
        else:
            emailNotifier.notifyFiles(paths, msg, report_name_wash)


def getAllFromFinance(report_hour, report_minutes, shiftedDay=0):
    """Получить все между датами"""
    currentDateTime = datetime.datetime.now()
    # Смещаем на нужный день
    currentDateTime = currentDateTime - datetime.timedelta(days=shiftedDay)
    currentDateTime = currentDateTime.replace(hour=report_hour, minute=report_minutes)
    currentTimeMinusDay = currentDateTime - datetime.timedelta(days=1)
    return (db.Finance
            .select()
            .where(db.Finance.date_time.between(currentTimeMinusDay, currentDateTime)))

if __name__ == "__main__":
    # Стандартный отчет
    currentTime = datetime.datetime.now()
    currentTime = currentTime.replace(hour=report_hour, minute=report_minutes)
    currentTimeMinusDay = currentTime - datetime.timedelta(days=1)
    currentTimeWithStartingWash = report_all_datetime_start

    data_csv_day = jinja_process(currentTimeMinusDay, currentTime, template_filename="oneDayForCsv.jinja2")
    data_pdf_day = jinja_process(currentTimeMinusDay, currentTime, template_filename="oneDayForPdf.jinja2")
    data_csv_all = jinja_process(currentTimeWithStartingWash, currentTime, template_filename="all.jinja2")
    data_pdf_all = jinja_process(currentTimeWithStartingWash, currentTime, template_filename="allDayForPdf.jinja2")

    rs = Reports()
    rs.add_report(Report('day', 'csv', data_csv_day))
    rs.add_report(Report('day', 'pdf', data_pdf_day))
    rs.add_report(Report('all', 'csv', data_csv_all))
    rs.add_report(Report('all', 'pdf', data_pdf_all))
    rs.send('Автоматические ежедневные отчеты.', theme=report_name_wash)

    s = sm.SettingsManager()
    s.stop()