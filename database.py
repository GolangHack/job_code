#!/usr/bin/env python
# coding=utf-8
import datetime
import logging
import mysql.connector as mariadb
import config
import time

log = logging.getLogger(__name__)


class Database:

    TYPE_DISCOUNT = 0
    TYPE_CREDIT = 1
    TYPE_OPERATOR = 2
    TYPE_ADMINISTRATOR = 3
    CONN_TRIALS = 5
    CONN_TRIAL_DELAY = 5

    def __init__(self, \
                 database_host, \
                 database_user, \
                 database_password, \
                 database_database \
                 ):
        # Database connection
        self._database_host = database_host
        self._database_user = database_user
        self._database_password = database_password
        self._database_database = database_database
        self.connectionChecked = False

        connectionTrials = 0
        while (connectionTrials < self.CONN_TRIALS) or self.connectionChecked:
            try:
                mariadb_connection = mariadb.connect(
                    user=self._database_user, password=self._database_password, database=self._database_database, host=self._database_host)
                cursor = mariadb_connection.cursor()
                self.connectionChecked = True
                cursor.close()
                mariadb_connection.close()
                break
            except mariadb.errors.InterfaceError as e:
                connectionTrials +=1
                log.info('Can not connect to database. Try to reconnect... %s', connectionTrials)
            except mariadb.errors.ProgrammingError as r:
                log.info(u"Не удалось получить досутп оп этим данным")
                print(r.message)
            time.sleep(self.CONN_TRIAL_DELAY)

        if connectionTrials >= self.CONN_TRIALS:
            log.critical('Can not established connection with database')

    def card_exist(self, uid):
        mariadb_connection = mariadb.connect(
            user=self._database_user, password=self._database_password, database=self._database_database, host=self._database_host)
        cursor = mariadb_connection.cursor()
        cursor.execute(
            "SELECT COUNT(*), balance, type FROM " + self._database_database  + ".card WHERE uid=%s;", (uid,))
        for row in cursor:
            if row[0] == 0:
                cursor.close()
                mariadb_connection.close()
                # Card does not exist
                return False
            else:
                cursor.close()
                mariadb_connection.close()
                # Card exists
                return True

    def card_insert(self, uid):
        mariadb_connection = mariadb.connect(
            user=self._database_user, password=self._database_password, database=self._database_database, host=self._database_host)
        cursor = mariadb_connection.cursor()
        log.info('Card %s does not exist. Adding card to database', uid)
        cursor.execute("INSERT INTO card (uid,balance,registration_date) VALUES (%s,%s,NOW());", (uid, 0,))
        mariadb_connection.commit()
        cursor.close()
        mariadb_connection.close()
        return self.card_info(uid)

    def card_info(self, uid):
        info = {'money':0,'type':'credit','description':'none','discount':0,'blocked':True}
        mariadb_connection = mariadb.connect(
            user=self._database_user, password=self._database_password, database=self._database_database, host=self._database_host)
        cursor = mariadb_connection.cursor()
        cursor.execute(
            "SELECT COUNT(*), balance, type, description, discount, blocked FROM " + self._database_database  + ".card WHERE uid=%s;", (uid,))
        for row in cursor:
            if row[0] != 0:
                pass
        cursor.close()
        mariadb_connection.close()

        if row[0] != 0:
            info['money'] = row[1]
            info['description'] = row[3]
            info['discount'] = row[4]
            info['blocked'] = (row[5] == 1)
            info['uid'] = uid
            if row[2] == Database.TYPE_DISCOUNT:
                info['type'] = 'discount'
            elif row[2] == Database.TYPE_CREDIT:
                info['type'] = 'credit'
            elif row[2] == Database.TYPE_OPERATOR:
                info['type'] = 'operator'
            elif row[2] == Database.TYPE_ADMINISTRATOR:
                info['type'] = 'administrator'
            return info
        else:
            return None

    def card_update(self, uid, money_delta, type_update):
        """
        Update money amount on the card. Increase or decrease
        depending on the sign of the parameter.
        Also put transaction at two tables (increasing and decreasing table)
        """
        mariadb_connection = mariadb.connect(
            user=self._database_user, password=self._database_password, database=self._database_database, host=self._database_host)
        cursor = mariadb_connection.cursor()

        if type_update == 'delta':
            # Add row into refill table
            if money_delta > 0:
                cursor.execute('''INSERT INTO refill (amount,event_date,card_uid,remaining)
                            VALUES ({0},NOW(),{1}, (select balance from card where uid = {1}) + {0})'''.format(money_delta, uid))
            # Add row into spent table
            if money_delta < 0:
                cursor.execute('''INSERT INTO spent (amount,event_date,card_uid, remaining)
                            VALUES ({0},NOW(),{1}, (select balance from card where uid = {1}) + {0})'''.format(money_delta, uid))
        # Get card balance
        cursor.execute(
            "SELECT COUNT(*), balance FROM " + self._database_database  + ".card WHERE uid=%s;", (uid,))

        for row in cursor:
            pass
        # Update card balance
        if type_update == 'delta':
            log.info('Update card %s ballance on delta %s', uid, money_delta)
            cursor.execute("UPDATE card SET balance=%s WHERE uid=%s", (row[1] + money_delta, uid))
        elif type_update == 'replace':
            log.info('Update card %s ballance on absolute amount %s', uid, money_delta)
            cursor.execute("UPDATE card SET balance=%s WHERE uid=%s", (money_delta, uid))

        mariadb_connection.commit()
        cursor.close()
        mariadb_connection.close()
        return self.card_info(uid)

    def getAllFromFinance(self, report_hour, report_minute):
        """Получает все данные в виде словаря из таблицы finance
        необходимой для формирования автоматических отчетов"""
        finance = []
        mariadb_connection = mariadb.connect(
            user=self._database_user, password=self._database_password, database=self._database_database,
            host=self._database_host)
        cursor = mariadb_connection.cursor(dictionary=True)
        # подготовка времени
        dtr = datetime.datetime.now()
        dtr = dtr.replace(hour=report_hour, minute=report_minute)
        sdtr = dtr.strftime("%Y-%m-%d %H:%M")

        cursor.execute("SELECT * FROM %s.finance WHERE (date_time > '%s' - INTERVAL 1 DAY) and (date_time < '%s');" % (
            self._database_database,
            sdtr,
            sdtr
        ))
        for row in cursor:
            finance.append(row)
        cursor.close()
        mariadb_connection.close()
        return finance

    def getWeryAllFromFinance(self, report_hour, report_minute, date_start='1997-08-14'):
        finance = []
        mariadb_connection = mariadb.connect(
            user=self._database_user, password=self._database_password, database=self._database_database,
            host=self._database_host)
        cursor = mariadb_connection.cursor(dictionary=True)
        dtr = datetime.datetime.now()
        dtr = dtr.replace(hour=report_hour, minute=report_minute)
        sdtr = dtr.strftime("%Y-%m-%d %H:%M")
        cursor.execute("SELECT * FROM %s.finance WHERE (date_time > ('%s')) and (date_time < ('%s'));" % (
            self._database_database,
            date_start,
            sdtr)
        )
        for row in cursor:
            finance.append(row)
        cursor.close()
        mariadb_connection.close()
        return finance

    def transaction(self, pay_transaction):
        source = pay_transaction['source']
        source_id = pay_transaction['source_id']
        dest = pay_transaction['dest']
        dest_id = pay_transaction['dest_id']
        source_card = pay_transaction['source_card']
        dest_card = pay_transaction['destination_card']
        source_type = pay_transaction['source_type']
        amount = pay_transaction['amount']
        selected_services = ";".join(map(str, pay_transaction['selected_services']))
        program_name = str(pay_transaction['program_number']) + ";" + pay_transaction['program_name'].encode("utf-8")
        program_price = pay_transaction['program_price']
        bills_dispensed = pay_transaction['bills_dispensed']
        money_from_cashback = pay_transaction['money_from_cashback']

        mariadb_connection = mariadb.connect(
            user=self._database_user, password=self._database_password, database=self._database_database, host=self._database_host)
        cursor = mariadb_connection.cursor()

        query = '''INSERT INTO finance (source,
                                                source_id,
                                                dest,
                                                dest_id,
                                                source_card,
                                                dest_card,
                                                source_type,
                                                amount,
                                                date_time,
                                                selected_services,
                                                program_name,
                                                program_price,
                                                bills_dispensed,
                                                money_from_cashback
                                                )
                    VALUES ({0},{1},{2},{3},{4},{5},{6},{7},NOW(),'{8}','{9}',{10},{11},{12})'''.format(source,
                                                                             source_id,
                                                                             dest,
                                                                             dest_id,
                                                                             source_card,
                                                                             dest_card,
                                                                             source_type,
                                                                             amount,
                                                                             selected_services,
                                                                             program_name,
                                                                             program_price,
                                                                             bills_dispensed,
                                                                             money_from_cashback
                                                                            )
        cursor.execute(query)
        mariadb_connection.commit()
        cursor.close()
        mariadb_connection.close()