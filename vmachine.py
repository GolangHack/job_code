#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import cStringIO
import datetime
import logging
import re
import time
import threading
from threading import BoundedSemaphore
from Queue import Queue, Empty
from pyutils.delay import Delay
from jinja2 import Environment, PackageLoader, select_autoescape
from atol.atol import Atol, AtolCommandException, PrinterStatus
import config
import json
from bankacquiring.bacquiring import BankAcquiring, BankAcquiringException
from yaml_config import YamlConfig
from scancodereader.scancodeReader import ScancodeReader
from qr_order import QrOrder
import subprocess

log = logging.getLogger(__name__)
raspberry_env = False
try:
    from rplclib.rplc import RaspeoPLC
    raspberry_env = True
except (ImportError, RuntimeError) as e:
    # If it is not a raspberry do not start some modules
    print u"Raspberry не был найден. Включаю режим эмуляции raspberry."

import serial
import pdfkit
from carddispenser.cardDispenser import CardDispenser, CardDispenserException
from operation_scenario import OperationScenario
from page_main import PageMain
from page_sel_program import PageSelProgram
from page_sel_service import PageSelService
from page_sel_pay import PageSelPay
from page_sel_balance import PageSelBalance
from page_pay_cash import PagePayCash
from page_pay_qr import PagePayQr
from page_card_close import PageCardClose
from page_check_printing import PageCheckPrinting
from page_bank_exchange import PageBankExchange
from page_client_card import PageClientCard
from page_card_balance import PageCardBalance
from page_want_print import PageWantPrint
from page_mifare_new import PageMifareNew
from page_exchange import PageExchange
from page_error import PageError
from page_error_bill_acceptor import PageErrorBillAcceptor
from page_warning import PageWarning
from page_warning_deprecated import PageWarningDeprecated
from page_input_sum import PageInputSum
from page_input_phone import PageInputPhone
from page_input_name import PageInputName
from page_input_access_code import PageInputAccessCode
from page_input_sum_manual_mode import PageInputSumManualMode
from page_bill_dispenser_failed import PageBillDispenserFailed
from page_queue_number import PageQueueNumber
from page_administrator_menu import PageAdministartorMenu
from page_config_editor import PageConfigEditor
from page_change_card import PageChangeCard
from page_report_control import PageReportControl
from page_company_reports import PageCompanyReports
from page_warning_clear_reports_buffer import PageWarningClearReportsBuffer
from page_warning_continue import PageWarningContinue
from page_not_correct_pincode import PageNotCorrectPincode
from page_license_access_text import PageLicenseAccessText
from page_add_phone_in_card import PageAddPhoneInCard
from page_error_phone_is_binded import PageErrorPhoneIsBinded
from page_bill_dispenser_take_change import PageBillDispenserTakeChange
from page_administrator_menu_bill_acceptor_and_dispenser import PageAdministartorMenuBillAcceptorAndDispenser
from page_error_with_timer import PageErrorWithTimer
from page_qr_code import PageQRCode
from page_operator_menu import PageOperatorMenu
from page_sleep_mode import PageSleepMode
from page_updater import PageUpdater
from gates import Gates, GatesStub
from robotcontroller import RobotController
from calendarEvents import CalendarEvents
from date_recovery import DateRecovery
from mbserialclient.mb_serial_client import ModbusSerialProvider, ModbusSerialProviderStub
from orderdisplay.orderDisplay import OrderDisplay, OrderDisplayStub
from leisuwash.leisuwash import LeisuWash, LeisuWashStub
from email_notifier import EmailNotifier
from utility import UtilityManager
from page_bank_pincode import PageBankPincode
import data_storage.database.Card as Card
import data_storage.database.Installation as Installation
import data_storage.database.FinanceTransaction as FinanceTransaction
import data_storage.database.Program as Program
import data_storage.database.CompanyReports as CompanyReports
import data_storage.database.models_generated as db
import data_storage.database.connection_manager as connection_manager
from uuid import uuid4 as uuid
import urllib2
from billkeeper.billAcceptor import BillAcceptor
from billkeeper.billAcceptorInterface import BillAcceptorInterface
from billkeeper.billDispenser import BillDispenser, BillDispenserException
import requests
from signals.signalfactory import SignalManager


class Vmachine(object):

    VERSION = 1
    'Pay source'
    PAY_SOURCE_BANK = 'bank'
    PAY_SOURCE_CLIENT_CARD = 'clientCard'
    PAY_SOURCE_CASH = 'cash'

    'Pay destination'
    PAY_DEST_CLIENT_CARD = 'client_card'
    PAY_DEST_ROBOT = 'robot'

    # Rack paramiters
    RACK_PLC = 0
    # Units
    UNIT_PLC = 0

    'Delays'
    PRINTER_ERROR_DELAY = 5

    'Display Address'
    DISPLAY1_ADDR = 25
    DISPLAY2_ADDR = 26

    '''Payment constants'''
    DEVICE_TERMINAL = 'terminal'
    DEVICE_POST = 'post'
    DEVICE_CLEANER = 'cleaner'

    """Client orders constant"""
    CLIENT_ORDER_PAID = 4
    CLIENT_ORDER_DONE = 2

    FCM_TEXT = {
        'QR_USED': u'QR код использован',
        'FAILED_TO_USE_QR': u'Не удалось использовать QR код',
        'BONUSES_ACCRUED': u'Вам начислены бонусы: ',
        'SERVICE_UNAVAILABLE': u'Один из выбранных сервисов недоступен. '
                               u'Вернитесь позже или отмените заказ.',
        'PRICE_MORE': u'Текущие цены услуг стоят дешевле, '
                      u'переплаченная сумма вернется на счет.',
        'PRICE_LESS': u'Сумма заказа не соответствует текущим '
                      u'ценам услуг на мойке.',
        'DONE_OR_CANCELED': u'Ваш заказ уже выполнен или отменен!',
        'QUEUE_NUMBER': u'Ваш номер очереди: ',
        'ROBOT_UNAVAILABLE': u'Робот недоступен.'
    }

    def __init__(self, be):
        self.be = be
        self.initOnCurrentConfig()
        self.initRegisterAllHtmlPages()
        self.mainPage.show()

    def initOnCurrentConfig(self):
        self._start_sleep_check = True
        self._card_data = None
        self.device = {self.DEVICE_TERMINAL:0, self.DEVICE_POST:1,self.DEVICE_CLEANER:2}
        self.pay_transaction = {'source':None, \
                            'source_id':None, \
                            'dest':None, \
                            'dest_id':None, \
                            'source_card':None, \
                            'dest_card':None, \
                            'source_type':None, \
                            'amount':None,  \
                            'date_time':None \
                            }
        self.versionRPLC = config.getProperty("versionRPLC", default=1, _type="int")
        self.signalManager = SignalManager()
        self.signalManager.createFromModel(model=db)
        'RPLC Rack initialization'
        if raspberry_env:
            self._rplc = RaspeoPLC(version=self.versionRPLC)
            self._rplc.setUserButtonHandler(1, self.onButton1CreateZReportNow)
            self._rplc.setUserButtonHandler(2, self.onButton2PrintZandXFromBuffer)
            self._rplc.setModulesHeartBeat(1, 1.5)
        else:
            self._rplc = None
        self.billAcceptorTypename = config.getProperty("bill_acceptor_typename", default="RplcVending")
        self.billAcceptorPort = config.getProperty("bill_acceptor_port", default="/dev/ttyACM0")
        self.billAcceptor = None
        self._dispenseBill = int(config.getProperty('dispense_bill'))
        self.billAcceptor = BillAcceptor.createByDriverName(
                                        self.billAcceptorTypename,
                                        self.onBill,
                                        self.onErrorBillAcceptor,
                                        self.onBillBusy,
                                        port = self.billAcceptorPort,
                                        rplc = self._rplc,
                                        recycleBill = self._dispenseBill)
        self.billAcceptor.init()
        self.billAcceptor.inhibitOn()
        'Switch mode button False - Print report True, False - clear buffer'
        self.switchModeOnPressButton2 = True
        self.timer_button_rplc = time.time()
        self.robots_count = config.getProperty('robots_count', _type="int")
        self.modbusSerialProvider = None
        self.leisuwash = [None] * self.robots_count
        self.gates = [None] * self.robots_count
        self.exitGates = [None] * self.robots_count
        self.orderDisplay = [None] * self.robots_count
        self.robotController = [None] * self.robots_count
        self.sideGateClosedDelay = config.getProperty('side_gate_closed_delay', 2, _type="int")
        self.sideGateQ = Queue()
        self.sideGateSemaphore = BoundedSemaphore(1)

        ''''''
        ''''''
        '''Create pages logix'''
        ''''''
        ''''''

        'Calendar backend'
        self.summer_start = config.getProperty('summer_start', _type="int")
        self.summer_end = config.getProperty('summer_end', _type="int")
        self.dayNightBySunset = config.getProperty('day_night_by_sunset', _type="bool")
        self.day_start = config.getProperty('day_start', _type="int")
        self.night_start = config.getProperty('night_start', _type="int")
        self.day_price_start = config.getProperty('day_price_start', _type="int")
        self.night_price_start = config.getProperty('night_price_start', _type="int")
        self.sleep_mode_allowed = config.getProperty('sleep_mode_allowed', default=False, _type="bool")

        self.gatesByTime = config.getProperty('gates_by_time', _type="bool")
        self.calendar = CalendarEvents(self.summer_start, \
                                       self.summer_end, \
                                       self.day_start,\
                                       self.night_start,\
                                       self.dayNightBySunset)

        self.priceCalendar = CalendarEvents(self.summer_start, \
                                       self.summer_end, \
                                       self.day_price_start,\
                                       self.night_price_start,\
                                       self.dayNightBySunset)
        dr = DateRecovery()
        dr.setRecoveryCallback(self.calendarEventsRecoveryCallback)
        self.operationScenario = OperationScenario(self.robots_count, self.calendar, self)
        self.calendar.registerChangeTimeOfDayHandler(self.timeOfDayChanged)
        'GENERAL'
        self.utilityManager = UtilityManager(self.calendar, self.priceCalendar)
        self.print_sleep_check = config.getProperty('print_sleep_check', _type='bool')
        self.queue_limit = config.getProperty("queue_limit", 99, _type='int')
        self.input_sum_limit = config.getProperty("input_sum_limit", 3, _type='int')
        services = Program.getServices()
        self.updater_enable = config.getProperty("updater_enable", default=False, _type='bool')
        'Регистрация сервисов из конфигов.'
        self.service_name = config.getProperty('service_name', _type="json")
        self.service_price_day = config.getProperty('service_price_day', _type="json")
        self.service_price_night = config.getProperty('service_price_night', _type="json")
        self.service_enablers = config.getProperty('service_enablers', _type="json")
        self.services_unavailability_for_individual_robots_enable = config.getProperty('services_unavailability_for_individual_robots_enable', default=False, _type="bool")
        self.availability_robotic_services = config.getProperty('availability_robotic_services', default=[1,1], _type="json")
        self.service_night_disabled = config.getProperty('service_night_disabled', _type="bool")

        for i, s in enumerate(services):
            self.utilityManager.registerUtility(Program.ServicePrice.PROGRAM_TYPE_NAME,
                                                i,
                                                s.name,
                                                s.dayPrice,
                                                s.nightPrice,
                                                s.allowed,
                                                self.service_night_disabled)

        'Регистрация программ из конфигов.'
        # Program.getPrograms()
        self.program_night_disabled = config.getProperty('program_night_disabled', _type='bool')
        self.program_name = config.getProperty('program_name', _type="json")
        self.program_description = []
        self.program_price_day = config.getProperty('program_price_day', _type="json")
        self.program_enablers = config.getProperty('program_enablers', _type="json")
        self.program_price_night = config.getProperty('program_price_night', _type="json")

        programs = Program.getPrograms()
        for i, p in enumerate(programs):
            self.program_description.append(self.toHtmlList(json.loads(p.description)))
            self.utilityManager.registerUtility(Program.ProgramPrice.PROGRAM_TYPE_NAME,
                                                i,
                                                p.name,
                                                p.dayPrice,
                                                p.nightPrice,
                                                p.allowed,
                                                self.program_night_disabled,
                                                p.hasOptions)


        'Кэшбек'
        self.client_card_price = config.getProperty('client_card_price', _type="int")
        self.client_card_cash_back_level =config.getProperty('client_card_cash_back_level', _type="json")
        self.client_card_cash_back_border =config.getProperty('client_card_cash_back_border', _type="json")

        self.gatesDaytimeOpened = config.getProperty('gates_daytime_opened', _type='bool')

        'PAY METHOD ENABLERS'
        self.pay_bank_disabled = config.getProperty('pay_bank_disabled', _type='bool')
        self.pay_cash_disabled = config.getProperty('pay_cash_disabled', _type='bool')
        self.pay_client_card_disabled = config.getProperty('pay_client_card_disabled', _type='bool')
        self.pay_qr_code_disabled = config.getProperty('pay_qr_code_disabled', _type='bool')

        self.pay_qr_enabled = config.getProperty('pay_qr_enabled', default=False, _type='bool')

        'OPERATION SCENARIO'
        self.operationScenario.registerPayHandler(self.processPayment)
        self.operationScenario.registerSaleHandler(self.saleHandler)
        self.operationScenario.registerCreateCompanyCard(self.createCompanyCard)
        self.operationScenario.registerAllCompanyCard(self.getAllCompanyCard)
        self.operationScenario.registerGetReportsByCard(self.getReportsByCard)
        self.operationScenario.registergetReportsClient(self.getReportsClient)
        self.operationScenario.registerCreateReportByCard(self.createReportByCard)
        self.operationScenario.registerCreateReportByClientId(self.createReportByClientId)
        self.operationScenario.registerSendEasyCompanyReport(self.sendCompanyReportToEmail)

        'Bill dispenser backend'
        self.operationScenario.registerDispenseBillHandler(self.dispenseBillHandler)
        self.operationScenario.setDispenseBill(self._dispenseBill)
        self.operationScenario.registerBillDispenserFailedHandler(self.billDispenserFailedHandler)

        'Card Dispenser backend'
        self.operationScenario.registerCardDispenserCheckStatusHandler(self.enquireCardDispenserHandler)
        self.operationScenario.setCardPrice(self.client_card_price)

        'ROBOT BACKEND'
        self.operationScenario.registerGetBetterRobotIndexHandler(self.getBetterRobotIndex)
        self.robot_smart_selection = config.getProperty('robot_smart_selection', _type='bool')
        self.operationScenario.setSmartSelection(self.robot_smart_selection)

        self.robot_maintenance = config.getProperty('robot_maintenance', _type="json")
        for i in range(self.robots_count):
            self.operationScenario.setRobotMaintenance(i, self.robot_maintenance[i])

        'Register cards and money enablers/disablers'
        self.operationScenario.registerReceiveMoneyEnabler(self.enableMoneyReceive)
        self.operationScenario.registerReceiveMoneyDisabler(self.disableMoneyReceive)
        self.operationScenario.registerReceiveCardsEnabler(self.enableCardsReceive)
        self.operationScenario.registerReceiveCardsDisabler(self.disableCarsdReceive)


        self.acquiring_emulate = config.getProperty('acquiring_emulate', _type="bool")
        self._atol_disabled = config.getProperty('atol_disabled', _type="bool")
        self.atolEnabled = not self._atol_disabled
        self.fiskal_check_disabled = config.getProperty('fiskal_check_disabled', default=False, _type="bool")
        self.checkAsQRCodeEnabled = config.getProperty("check_as_qr_code_enabled",
                                                       default=False,
                                                       _type="bool")
        self.atol_nds_type = config.getProperty("atol_nds_type", 6, _type='int')
        self.atol_type_sno = config.getProperty("atol_type_sno", 8, _type='int')

        self._print_errors = config.getProperty('print_errors', _type='bool')
        self._acquiring_client_card_disabled = config.getProperty('acquiring_client_card_disabled', _type='bool')

        self.sber_client_id = config.getProperty('sber_client_id')
        self.sber_client_secret = config.getProperty('sber_client_secret')
        self.sber_member_id = config.getProperty('sber_member_id')
        self.sber_id_qr = config.getProperty('sber_id_qr')

        'load from config database parameters'
        self.database_host = config.getProperty('database_host')
        self.database_user = config.getProperty('database_user')
        self.database_password = config.getProperty('database_password')
        self.database_database = config.getProperty('database_database')

        'Load from config modbus and robot parameters'
        self.modbus_port_count = config.getProperty('modbus_port_count', _type='int', default=1)
        self.modbus_emulate = config.getProperty('modbus_emulate', _type='bool')
        self.robot_emulate = config.getProperty('robot_emulate', _type='bool')
        self.display_emulate = config.getProperty('display_emulate', _type='bool')
        self.card_dispenser_emulate = config.getProperty('card_dispenser_emulate', _type='bool')
        self.gates_emulate = config.getProperty('gates_emulate', _type='bool')
        self.robot_queue_enabled = config.getProperty('robot_queue_enabled', _type='bool')
        self.exit_gates_disabled = config.getProperty("exit_gates_disabled", True, 'bool')
        self.exit_gates_emulate = config.getProperty("exit_gates_emulate", True, 'bool')
        self.sideGateDisabled = config.getProperty('side_gate_disabled', True, 'bool')
        self.sideGateEmulate = config.getProperty('side_gate_emulate', True, 'bool')

        'Входные'
        self.gate_open_output = config.getProperty('gate_open_output', _type="json")
        self.gate_close_output = config.getProperty('gate_close_output', _type="json")

        'Выездные'
        self.exit_gate_open_output = config.getProperty('exit_gate_open_output', "[4, 6]", "json")
        self.exit_gate_close_output = config.getProperty('exit_gate_close_output', "[5, 7]", "json")

        'Боковые'
        self.sideGateOpenOutput = config.getProperty('side_gate_open_output', [33], "json")
        self.sideGateSensorInput = config.getProperty('side_gate_sensor_input', 1, _type='int')
        self.sideGateInputMask = 1 << self.sideGateSensorInput
        self.lastSideGateInputState = None
        self.robot_mb_address = config.getProperty('robot_mb_address', _type="json")
        self.display_mb_address = config.getProperty('display_mb_address', _type="json")
        self.open_side_gate_with_exit_gate = config.getProperty('open_side_gate_with_exit_gate',
                                                                default=False, _type=bool)

        'Шлагбаум'
        self.barrierClosedDelay = config.getProperty('barrier_closed_delay', default=2, _type='int')
        self.barrierEnabled = config.getProperty('barrier_enabled', default=False, _type='bool')
        self.barrierOpenOutput = config.getProperty('barrier_open_output', default=[2], _type='json')
        self.barrierInviteDelay = config.getProperty('barrier_invite_delay', default=10, _type='int')
        self.barrierSensorInput = config.getProperty('barrier_sensor_input', default=1, _type='int')
        self.barrierSensorInputMask = 1 << self.barrierSensorInput
        self.barrierLastInputState = None
        self.barrierSemaphore = BoundedSemaphore(1)
        self.barrierQueue = Queue()

        if self.modbus_port_count == 1:
            self.mb_port = config.getProperty('mb_port')
        else:
            self.mb_port = config.getProperty('mb_port', _type="json")
        self.mb_speed = config.getProperty('mb_speed', _type="json")

        'load from config washer parameters'
        self._terminal_id = config.getProperty('terminal_id', _type="int")
        self._acquiring_ip = config.getProperty('acquiring_ip')

        self.pageError = self.be.createPage(PageError, "error.html",
                                            operationScenario=self.operationScenario,
                                            phone_number=config.getProperty('admin_phone'))

        'Database Initialization'
        log.info("(vmachine)Starting database")

        'Bill dispenser initialization'
        self.billDispenserTypename = config.getProperty("bill_dispenser_typename", default="Lcdm1")
        self.billDispenserPort = config.getProperty("bill_dispenser_port",
                                                    default="/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AM007Q4C-if00-port0")
        log.info('Initialization bill dispenser...')
        self.billDispenser = BillDispenser.createByDriverName(self.billDispenserTypename,
                                                              self.billAcceptor,
                                                              port = self.billDispenserPort)
        try:
            "Тестируем на возможность выдачи сдачи"
            self.billDispenser.init()
        except BillDispenserException:
            'Выводить экран об ошибке'
            self.pageError.show(
                error_text=u"Произошла ошибка при инициации купюроразменника %s " % self.billDispenserTypename
            )

        self.crt541_port = config.getProperty('crt541_port')
        self.cardDispenserType = config.getProperty('card_dispenser_type', 'Crt541')
        print("value self.cardDispenserType")
        print(self.cardDispenserType)
        'Card dispenser Initialization'
        if raspberry_env and not self.card_dispenser_emulate:
            log.info('Card dispenser initialization')
            self.cardDispenser = CardDispenser.createByDriverName(self.cardDispenserType, self.crt541_port)
            self.cardDispenser.reset()
        else:
            self.cardDispenser = None
        self.atol_mode_only_qr_code_check = config.getProperty("atol_mode_only_qr_code_check", default=False, _type="bool")
        kaznacheyEquipment = db.Equipment.get(db.Equipment.name == 'KKM')
        kaznacheySignals = self.signalManager.getByEquipment(kaznacheyEquipment.id)
        'KKM Initialization'
        if not self._atol_disabled:
            log.info("Starting ATOL")
            # См. константы PRINTER_ в модуле Atol. 1 - memory, 0 - T680
            printer = 1 if self.atol_mode_only_qr_code_check else 0
            self.kkm = Atol(self._atol_disabled,
                            atolVersion=config.getProperty("atol_version", 13, _type='int'),
                            printer=printer, signals=kaznacheySignals)
        else:
            self.kkm = None
        self.isKkmFiscal = self.getKkmGetStatusFiscalization()
        self.printServiceCheckEnabled = config.getProperty('atol_print_service_check_enabled',
                                                           default=True,
                                                           _type='bool')
        acquiring_python_start = config.getProperty("acquiring_python_start", default=False, _type="bool")

        'Bank acquiring initialization'
        if not self.acquiring_emulate:
            log.info("Starting Acquiring...")
            try:
                if raspberry_env:
                    self._bacq = BankAcquiring(self.bankacquiringHanler,
                                               self._terminal_id,
                                               self._acquiring_ip,
                                               10400,
                                               config.getProperty('acquiring_path_service') if acquiring_python_start else None)
                    log.info("Acquiring started successfully")
                else:
                    self._bacq = BankAcquiring(self.bankacquiringHanler,
                                               self._terminal_id,
                                               self._acquiring_ip,
                                               10400,
                                               config.getProperty('acquiring_local_path_service') if acquiring_python_start else None)
                    log.info("Local acquiring started successfully")

            except BankAcquiringException as e:
                log.critical("Can not start acquiring... Switch on emulating... Rised exception: %s", str(e))
                self.acquiring_emulate = True
                self.pay_bank_disabled = True
                print "BANK ACQ ERROR"


        sender = config.getProperty('email_sender')
        pwd = config.getProperty('email_pwd')
        receivers = config.getProperty('email_receivers', _type="json")
        serv = config.getProperty('email_server')
        self.emailNotifier = EmailNotifier(sender, receivers, serv, sender, pwd)
        self.emailNotifierEnabled = config.getProperty('email_notifier_enabled', False, 'bool')


        'Modbus Devices backend'
        if self.modbus_emulate:
            self.modbusSerialProvider = ModbusSerialProviderStub(self.mb_port,
                                                                 speed = self.mb_speed,
                                                                 mode = ModbusSerialProvider.ASCII,
                                                                 parity = serial.PARITY_EVEN,
                                                                 stopBits = serial.STOPBITS_ONE,
                                                                 serialDataLen = serial.SEVENBITS)
        else:
            # self.modbusSerialProvider = ModbusSerialProvider(self.mb_port,
            #                                                  speed = int(self.mb_speed),
            #                                                  parity = serial.PARITY_EVEN,
            #                                                  stopBits = serial.STOPBITS_ONE,
            #                                                  serialDataLen = serial.SEVENBITS)
            if self.modbus_port_count == 1:
                self.modbusSerialProvider = ModbusSerialProvider(self.mb_port,\
                                                                 speed = int(self.mb_speed),\
                                                                 mode = ModbusSerialProvider.ASCII,\
                                                                 parity = serial.PARITY_EVEN,\
                                                                 stopBits = serial.STOPBITS_ONE,\
                                                                 serialDataLen = serial.SEVENBITS)
            else:
                self.modbusSerialProvider = []
                for i in range(self.modbus_port_count):
                    if self.open_side_gate_with_exit_gate:
                        log.info('self.mb_port[i]: {}'.format(self.mb_port[i]))
                    self.modbusSerialProvider.append(
                        ModbusSerialProvider(self.mb_port[i],
                                             speed=int(self.mb_speed),
                                             mode=ModbusSerialProvider.ASCII,
                                             parity=serial.PARITY_EVEN,
                                             stopBits=serial.STOPBITS_ONE,
                                             serialDataLen=serial.SEVENBITS))

        self._gate_impulse_time = config.getProperty('gate_impulse_time', _type="int")
        reverse_exit = config.getProperty("reverse_exit", default=False, _type="bool")
        print "reverse_exit ", reverse_exit
        for i in range(self.robots_count):
            if self.robot_emulate:
                self.leisuwash[i] = LeisuWashStub(self.modbusSerialProvider, 0, 'LeisuwashStub ' + str(i+1) + ' ')
            else:
                if self.modbus_port_count == 1:
                    self.leisuwash[i] = LeisuWash(self.modbusSerialProvider,
                                                  int(self.robot_mb_address[i]),
                                                  'Leisuwash ' + str(i+1) + ' ',
                                                  reverseExit = reverse_exit)
                else:
                    self.leisuwash[i] = LeisuWash(self.modbusSerialProvider[i],
                                                  int(self.robot_mb_address[i]),
                                                  'Leisuwash ' + str(i + 1) + ' ',
                                                  reverseExit=reverse_exit)
                self.operationScenario.registerIsRobotAllowedHandler(self.isRobotAllowed, i)
                # self.leisuwash[i] = LeisuWash(self.modbusSerialProvider, , 'Leisuwash ' + str(i) + ' ')
            'Входные ворота'
            log.info('Leisuwash {} is initialized as {} type'.format(str(i), type(self.leisuwash[i])))
            if self.gates_emulate:
                self.gates[i] = GatesStub('GatesStub ' + str(i+1) + ' ')
            else:
                self.gates[i] = Gates('Gates ' + str(i+1) + ' ')
            self.gates[i].registerCloseGatesHandler(self.closeGatesHandler, i)
            self.gates[i].registerOpenGatesHandler(self.openGatesHandler, i)
            'Выходные ворота'
            if not self.exit_gates_disabled:
                if self.exit_gates_emulate:
                    self.exitGates[i] = GatesStub('ExitGatesStub ' + str(i+1) + ' ')
                else:
                    self.exitGates[i] = Gates('ExitGates ' + str(i + 1) + ' ')
                self.exitGates[i].registerCloseGatesHandler(self.closeExitGatesHandler, i)
                self.exitGates[i].registerOpenGatesHandler(self.openExitGatesHandler, i)

            'При потере соединения по mudbus - открыть ворота'
            if config.getProperty('openGateIfLostConnectByMudbus', False, _type='bool'):
                pass # TODO сделать правильно, через robot controller (ф-я _checkGood должна возвращать список и в
                # if self._checkGood():  сохранть в тупль, чтобы в elif not self._error_trig: обработать две систуации).
            if self.display_emulate:
                self.orderDisplay[i] = OrderDisplayStub(self.modbusSerialProvider,
                                                        self.display_mb_address[i],
                                                        'DisplayStub ' + str(i+1) + ' ',
                                                        self.robot_smart_selection)
            else:
                if self.modbus_port_count == 1:
                    self.orderDisplay[i] = OrderDisplay(self.modbusSerialProvider,
                                                        self.display_mb_address[i],
                                                        'Display ' + str(i+1) + ' ',
                                                        self.robot_smart_selection)
                else:
                    self.orderDisplay[i] = OrderDisplay(self.modbusSerialProvider[0],
                                                        self.display_mb_address[i],
                                                        'Display ' + str(i + 1) + ' ',
                                                        self.robot_smart_selection)

            closeEntryGate = config.getProperty("close_entry_gate_on_car_enter",
                                                default = True, _type="bool")
            inviteDelay = config.getProperty('invite_delay', default=10, _type='int')
            entryGateClosingDelay = config.getProperty('entry_gate_closing_delay', default=30, _type='int')
            robot = Installation.Robot(number=i + 1)
            robotSignals = self.signalManager.getByInstallation(robot.id)
            self.robotController[i] = RobotController(
                robotNumber=i,
                calendar=self.calendar,
                modbusSerialProvider=self.modbusSerialProvider,
                entryGate=self.gates[i],
                orderDisplay=self.orderDisplay[i],
                leisuWash=self.leisuwash[i],
                entryGateClosingDelay=entryGateClosingDelay,
                open_side_gate_with_exit_gate=self.open_side_gate_with_exit_gate,
                description='Robot Controller ' + str(i+1) + ': ',
                queue_limit=self.queue_limit,
                inviteDelay=inviteDelay,
                exitGate=self.exitGates[i],
                closeEntryGateOnCarEnter=closeEntryGate,
                smart_queue_enabled=self.robot_smart_selection,
                signals=robotSignals
            )
            self.robotController[i].registerOnErrorHandler(self.onRobotError, i)
            self.robotController[i].setGatesDaytimeOpened(self.gatesDaytimeOpened)
            self.robotController[i].registerProgramCountDbHandler(self._syncProgramCountDb)

        if (not self.sideGateDisabled) and (not self.sideGateEmulate):
            sideGateModule = self.sideGateSensorInput >> 4
            self._rplc.module[sideGateModule].setOnInputChangedHandler(self.onSideGateInputChanged)
        if self.barrierEnabled:
            self._rplc.module[(self.barrierSensorInput >> 4)]\
                .setOnInputChangedHandler(self.onBarrierSensorInputStateChanged)
        self.companyReports = CompanyReports.CompanyReports()
        self.manual_mode_allowed = config.getProperty("manual_mode_allowed",
                                                      default=False,
                                                      _type="bool")

        """Sms gate & access code"""
        self.enableSmsGatePinCode = config.getProperty("enable_sms_gate_pin_code", default=False)
        print "self.enableSmsGatePinCode: " + str(self.enableSmsGatePinCode)
        self.accessCodeMaxTrails = config.getProperty("access_code_max_trails", default=3, _type="int")
        self.smsGateLogin = config.getProperty("sms_gate_login", default="z1586431990686")
        self.smsGatePassword = config.getProperty("sms_gate_password", default="")
        # todo smsGateGost не используется
        self.smsGateHost = config.getProperty("sms_gate_host", default="")
        self.licenseTextPersonalDataProcessing = config.getProperty("license_text_personal_data_processing",
                                                                    default=u"Текст соглашения на обработку персональных данных")
        self.licenseTextAdwDataAgreement = config.getProperty("license_text_adw_data_agreement",
                                                              default=u"Текст соглашения на рассылку данных")
        self.requestPhoneForClientCardEnabled = config.getProperty("requestPhoneForClientCardEnabled",
                                                                  default=True, _type="bool")

        self.codePhoneCounrty = config.getProperty("code_phone_country", default="7")
        self.lenghtPhoneNumber = config.getProperty("lenght_phone_number", default=10, _type="int")

        self.mainPageTextButtonClientCard = config.getProperty("main_page_text_button_client_card",
                                                               default=u"Клиентская карта")
        self.drawTestQrCodeEnabled = config.getProperty("draw_test_qr_code_enabled",
                                                        default=False,
                                                        _type="bool")
        self.dryZoneDisabled = config.getProperty("dry_zone_disabled",
                                                  default=False,
                                                  _type="bool")
        self.isPinPadAvailable = config.getProperty("is_pin_pad_available", default=False, _type="bool")

        self.scancodeReader = []
        self.scancodeReaderCount = config.getProperty('scancode_reader_count', _type='int',
                                                      default=self.robots_count)
        self.scancodeReaderPort = config.getProperty('scancode_reader_port',
                                                     '["/dev/ttyACM0", "/dev/ttyACM1"]', _type='json')
        self.scancodeReaderEnabled = config.getProperty('scancode_reader_enabled',
                                                        default=False, _type='bool')
        if self.scancodeReaderEnabled:
            for i in range(self.scancodeReaderCount):
                self.scancodeReader.append(ScancodeReader(self.scancodeReaderPort[i],
                                                          baudrate=115200))
                self.scancodeReader[i].setOnCodeReadHandler(self.onCodeReadHandler,
                                                            reader_number=i)

        self.yamlConfig = YamlConfig(source='config.yml')

        self.firebase_url = ':'.join([self.yamlConfig.get('firebase', 'host'),
                                      self.yamlConfig.get('firebase', 'port')])
        self.robotcarwashrest_url = ':'.join([self.yamlConfig.get('robotcarwashrest', 'host'),
                                              self.yamlConfig.get('robotcarwashrest', 'port')])
        self.wash_id = self.yamlConfig.get('terminal', 'wash_id')
        self.wash_key = self.yamlConfig.get('terminal', 'wash_key')


    def initRegisterAllHtmlPages(self):
        """Регистрация используемых html страниц"""
        phone_number = config.getProperty('admin_phone')
        self.pageError = self.be.createPage(PageError, "error.html", operationScenario=self.operationScenario,
                                            phone_number=phone_number)
        self.mainPage = self.be.createPage(PageMain,
                                           "main.html",
                                           smart_selection_enabled=self.robot_smart_selection,
                                           operationScenario=self.operationScenario,
                                           robotController=self.robotController,
                                           mainPageTextButtonClientCard=
                                           self.mainPageTextButtonClientCard,
                                           phone_number=phone_number,
                                           robotsCount=self.robots_count,
                                           manualModeAllowed=self.manual_mode_allowed)
        sel_program_name = "sel_program.html"
        if config.getProperty("count_programs", default=4, _type="int") == 3:
            sel_program_name = "sel_program_3.html"
        self.be.createPage(PageSelProgram, sel_program_name, \
                           utilityManager=self.utilityManager, \
                           operationScenario=self.operationScenario, \
                           program_description=self.program_description, \
                           night_start = self.night_price_start, \
                           night_stop = self.day_price_start, \
                           programs_night_disabled=self.program_night_disabled,
                           phone_number=phone_number)
        self.be.createPage(PageSelService, "sel_service.html", service_name = self.service_name, \
                           utilityManager=self.utilityManager, \
                           operationScenario=self.operationScenario, \
                           phone_number=phone_number)
        self.be.createPage(PageSelPay, "sel_pay.html", \
                           pay_bank_disabled=self.pay_bank_disabled, \
                           pay_cash_disabled=self.pay_cash_disabled, \
                           pay_client_card_disabled=self.pay_client_card_disabled, \
                           operationScenario=self.operationScenario, phone_number=phone_number,
                           pay_qr_enabled=self.pay_qr_enabled)

        self.payment_emulate = config.getProperty('payment_emulate', _type="bool")
        self.pagePayCash = self.be.createPage(PagePayCash, "pay_cash.html", operationScenario=self.operationScenario, paymentEmulate = self.payment_emulate, phone_number = phone_number)
        self.be.createPage(PageClientCard, "client_card.html", price=self.client_card_price,
                           operationScenario=self.operationScenario, phone_number=phone_number,
                           cardDispenserEmulate=self.card_dispenser_emulate)

        self.pageCardClose = self.be.createPage(PageCardClose,
                                                "card_close.html",
                                                operationScenario=self.operationScenario,
                                                emulate=self.acquiring_emulate,
                                                emulate_client_card=config.getProperty("emulate_client_card", False, _type='bool'),
                                                phone_number = phone_number)
        self.be.createPage(PagePayQr, "pay_qr.html", operationScenario=self.operationScenario, phone_number = phone_number)
        # Временно заменим стандартный хендлер
        self.operationScenario.registerCardEventHandler(self.pageCardClose.cardEvent)

        self.be.createPage(PageCheckPrinting, "check_printing.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.pageBankExchange = self.be.createPage(PageBankExchange, "bank_exchange.html", operationScenario=self.operationScenario, phone_number = phone_number, pay_qr_enabled=self.pay_qr_enabled)
        self.be.createPage(PageSelBalance, "sel_balance.html", \
                           operationScenario=self.operationScenario, \
                           kkm=self.kkm, \
                           phone_number = phone_number)
        self.be.createPage(PageWantPrint, "want_print.html", operationScenario=self.operationScenario, atol_print_service_check_enabled = self.printServiceCheckEnabled, phone_number = phone_number)
        self.be.createPage(PageCardBalance, "card_balance.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageMifareNew, "mifare_new.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageExchange, "exchange.html", operationScenario=self.operationScenario, phone_number = phone_number)

        self.PageWarningDeprecated = self.be.createPage(PageWarningDeprecated, "warning_deprecated.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageInputSum, "input_sum.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageInputPhone, "input_phone.html", operationScenario=self.operationScenario, phone_number = phone_number, code_phone_counrty=self.codePhoneCounrty, lenght_phone_number=self.lenghtPhoneNumber)
        self.be.createPage(PageInputName, "input_name.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageInputSumManualMode, "input_sum_manual_mode.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageInputAccessCode, "input_access_code.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageBillDispenserFailed, "bill_dispenser_failed.html", operationScenario=self.operationScenario, phone_number = phone_number)
        advertising_text = config.getProperty('advertising_text')
        show_advertising_text = config.getProperty('show_advertising_text', default=False, _type="bool")
        self.be.createPage(PageQueueNumber, "queue_number.html", operationScenario=self.operationScenario, advertising_text = advertising_text, show_advertising_text = show_advertising_text, phone_number = phone_number, robots_count=self.robots_count)
        self.be.createPage(PageAdministartorMenu, "administrator_menu.html",
                           operationScenario=self.operationScenario,
                           phone_number=phone_number,
                           updater_enable=self.updater_enable)
        self.be.createPage(PageConfigEditor, "config_editor.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageChangeCard, "page_change_card.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageReportControl, "page_report_control.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageCompanyReports, "page_company_reports.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.pageWCRBuffer = self.be.createPage(PageWarningClearReportsBuffer, "warning_clear_reports_buffer.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageNotCorrectPincode, "not_correct_pincode.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageLicenseAccessText, "license_access_text.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageAddPhoneInCard, "add_phone_in_card.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageErrorPhoneIsBinded, "error_phone_is_binded.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageQRCode, "page_qr_code.html", operationScenario=self.operationScenario, advertising_text = advertising_text, show_advertising_text = show_advertising_text, phone_number = phone_number)
        self.pageErrorWithTimer = self.be.createPage(PageErrorWithTimer, "error.html", operationScenario=self.operationScenario, phone_number = phone_number)
        self.be.createPage(PageWarningContinue, "warning_continue.html", operationScenario=self.operationScenario, phone_number=phone_number)
        sleep_mode_text = config.getProperty('sleep_mode_text')
        self.be.createPage(PageSleepMode, "sleep_mode.html", operationScenario=self.operationScenario, phone_number=phone_number, sleep_mode_text=sleep_mode_text)
        self.be.createPage(PageUpdater, "updater.html", operationScenario=self.operationScenario, phone_number=phone_number)
        self.pageErrorBillAcceptor = self.be.createPage(PageErrorBillAcceptor,
                                                        "error_bill_acceptor.html",
                                                        operationScenario=self.operationScenario,
                                                        phone_number=phone_number)

        self.pageBillDispenserTakeChange = self.be.createPage(PageBillDispenserTakeChange,
                                                        "bill_dispenser_despense_bill.html",
                                                        operationScenario=self.operationScenario,
                                                        phone_number=phone_number)

        self.pageAdministartorMenuBillAcceptorAndDispenser = self.be.createPage(
            PageAdministartorMenuBillAcceptorAndDispenser,
            "administrator_menu_bill_acceptor_and_dispenser.html",
            operationScenario=self.operationScenario,
            recycler=self.billAcceptor.canRecycle() if self.billAcceptor else None,
            phone_number=phone_number)

        self.be.createPage(PageWarning, "warning.html", operationScenario=self.operationScenario, phone_number=phone_number)

        self.be.createPage(PageOperatorMenu, 'operator_menu.html', robotsCount=self.robots_count,
                           robotController=self.robotController, phone_number=phone_number,
                           operationScenario=self.operationScenario)

        self.be.createPage(PageBankPincode, "bank_pincode.html",
                           operationScenario=self.operationScenario, phone_number=phone_number)

    def toHtmlList(self, lst):
        out = u"<ul>"
        for u in lst:
            out += u"<li>{}</li>".format(u)
        out += u"</ul>"
        return out

    'Управление буффером z и x отчетов. Атол.'
    def createZReportInBuffer(self):
        if not self._atol_disabled:
            self.kkm.reportZ()
            log.info("Report Z Create.")
        else:
            log.warning("Report Z will be not created. Emulator mode Atol.")

    def clearBufferZandXReport(self):
        if not self._atol_disabled:
            try:
                self.kkm.clearBufferReports()
                log.info("Cleared buffer.")
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))
        else:
            log.warning("Will be not cleared buffer. Emulator mode Atol.")

    def printBufferZandXReport(self):
        if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                self.atolEnabled and
                self.operationScenario.getHasPaper()):
            try:
                self.kkm.printFromBufferReports()
                log.info("Print Z and X report from buffer.")
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))
        elif self.operationScenario.atolModeOnlyQrCodeCheck() and self.atolEnabled:
            log.warning("Will not be printed from buffer. Atol mode: ONLY QR CHECK.")
        elif not self.operationScenario.getHasPaper() and self.atolEnabled:
            log.warning("Will not be printed from buffer. Reason: PAPER IS OUT.")
        else:
            log.warning("Will not be printed from buffer. Atol mode: EMULATION.")

    'Обработчики нажатий на кнопки контроллера rplc'
    def onButton1CreateZReportNow(self):
        if ((time.time() - self.timer_button_rplc) > 10):
            log.info("Button 1 pressed")
            try:
                self.createZReportInBuffer()
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))
            self.timer_button_rplc = time.time()
        else:
            print("WARNING! Button is occupied")

    def onButton2PrintZandXFromBuffer(self):
        if ((time.time() - self.timer_button_rplc) > 10):
            log.info("Button 2 pressed")
            if not self._atol_disabled:
                self.pageWCRBuffer.show()
            self.timer_button_rplc = time.time()
        else:
            print("WARNING! Button is occupied")

    def onRobotError(self, description, robotID):
        def sender():
            self.emailNotifier.notify(description)

        if self.emailNotifierEnabled is True:
            threading.Thread(target=sender).start()

    def getBetterRobotIndex(self, *args, **kwargs):
        queue_size = []
        for robot_index in range(self.robots_count):
            if (self.operationScenario.getRobotMaintenance(robot_index) == 0
                    and self.isRobotAllowed(robot_index)):
                queue_size.append(self.robotController[robot_index].getCarsInQueue())
            else:
                queue_size.append(100)
        if sum(queue_size) == self.robots_count * 100:
            better_robot_index = None
        else:
            better_robot_index = queue_size.index(min(queue_size))
        log.info(u'Select better robot index: {}'.format(better_robot_index))
        return better_robot_index

    def timeOfDayChanged(self, timeOfDay):
        ' operate gates on time of day change'
        if timeOfDay == CalendarEvents.DAY:
            if self.sleep_mode_allowed:
                self.be.switchPageByName('PageMain')
            if self.gatesByTime:
                log.info("It's time to open the gates")
                for i in range(self.robots_count):
                    self.openGatesHandler(i)
        elif timeOfDay == CalendarEvents.NIGHT:
            if self.sleep_mode_allowed and self.operationScenario.canGoToSleepMode:
                self.be.switchPageByName('PageSleepMode')
            if self.gatesByTime:
                log.info("It's time to close the gates")
                for i in range(self.robots_count):
                    self.closeGatesHandler(i)

    def calendarEventsRecoveryCallback(self):
        self.calendar.updateActualData()
        self.priceCalendar.updateActualData()

    def getGatesData(self, gates, robotIndex):
        """Возвращает [номер модуля, номер пина]"""
        return [(gates[robotIndex] & 0xF0) >> 4, gates[robotIndex] & 0xF]

    'Входные ворота'
    def openGatesHandler(self, robotIndex, *args, **kwargs):
        log.debug("Open gate impulse for robot{}".format(robotIndex))
        mod, pin = self.getGatesData(self.gate_open_output, robotIndex)
        def disOpenContact():
            self._rplc.module[mod].setOutput(pin, False)
        threading.Timer(self._gate_impulse_time, disOpenContact).start()
        self._rplc.module[mod].setOutput(pin, True)

    def closeGatesHandler(self, robotIndex, *args, **kwargs):
        log.debug("Close gate impulse for robot{}".format(robotIndex))
        mod, pin = self.getGatesData(self.gate_close_output, robotIndex)
        def disCloseContact():
            self._rplc.module[mod].setOutput(pin, False)
        threading.Timer(self._gate_impulse_time, disCloseContact).start()
        self._rplc.module[mod].setOutput(pin, True)

    'Выездные ворота'
    def openExitGatesHandler(self, robotIndex, *args, **kwargs):
        log.debug("Open exit gate impulse for robot{}".format(robotIndex))
        mod, pin = self.getGatesData(self.exit_gate_open_output, robotIndex)
        def disOpenContact():
            self._rplc.module[mod].setOutput(pin, False)
        threading.Timer(self._gate_impulse_time, disOpenContact).start()
        self._rplc.module[mod].setOutput(pin, True)
        if 'openSideGate' in kwargs:
            if kwargs['openSideGate'] is True:
                if self.open_side_gate_with_exit_gate:
                    self.openSideGate(robotIndex)
                else:
                    if self.sideGateSemaphore.acquire(blocking=False):
                        self.openSideGate(robotIndex)
                    else:
                        self.sideGateQ.put(robotIndex)
                        logging.info('Put robot{} into sideGateQ'.format(robotIndex + 1))

    def closeExitGatesHandler(self, robotIndex, *args, **kwargs):
        log.debug("Close exit gate impulse for robot{}".format(robotIndex))
        mod, pin = self.getGatesData(self.exit_gate_close_output, robotIndex)
        def disCloseContact():
            self._rplc.module[mod].setOutput(pin, False)
        threading.Timer(self._gate_impulse_time, disCloseContact).start()
        self._rplc.module[mod].setOutput(pin, True)

    'Боковые ворота'
    def openSideGate(self, robotIndex, *args, **kwargs):
        logging.info('SideGate open for robot{}'.format(robotIndex + 1))
        mod, pin = self.getGatesData(self.sideGateOpenOutput, 0)
        def disOpenContact():
            self._rplc.module[mod].setOutput(pin, False)
        threading.Timer(self._gate_impulse_time, disOpenContact).start()
        self._rplc.module[mod].setOutput(pin, True)

    def onSideGateInputChanged(self, module, state):
        currSideGateInputState = (state[0] & self.sideGateInputMask)
        if currSideGateInputState != self.lastSideGateInputState:
            logging.info('SideGate input state changed to {}'.format(currSideGateInputState))
            self.lastSideGateInputState = currSideGateInputState
            if currSideGateInputState == 0: # todo: Вынести в переменную сравнение с нулем
                Delay().once(self.sideGateClosedDelay, self.onSideGateClosed)

    def onSideGateClosed(self):
        logging.info('Side gate closed')
        if not self.open_side_gate_with_exit_gate:
            try:
                robot = self.sideGateQ.get(block=False)
                logging.info('Get robot{} from sideGateQ'.format(robot + 1))
                self.openSideGate(robot)
            except Empty:
                try:
                    self.sideGateSemaphore.release()
                except ValueError:
                    return

    def openBarrierOrPutIntoQueue(self, queue_number, *args, **kwargs):
        if self.barrierSemaphore.acquire(blocking=False):
            self.openBarrier(queue_number, *args, **kwargs)
        else:
            log.info('Put queue number {} into BarrierQueue'.format(queue_number))
            self.barrierQueue.put(queue_number)

    def openBarrier(self, queue_number, *args, **kwargs):
        log.info('Barrier open for queue number {}'
                 .format(queue_number))
        mod, pin = self.getGatesData(self.barrierOpenOutput, 0)
        def disOpenContact():
            self._rplc.module[mod].setOutput(pin, False)
        threading.Timer(self._gate_impulse_time, disOpenContact).start()
        self._rplc.module[mod].setOutput(pin, True)

    def onBarrierSensorInputStateChanged(self, module, state):
        currSensorState = (state[0] & self.barrierSensorInputMask)
        if currSensorState != self.barrierLastInputState:
            log.info('Barrier sensor input state changed: {}'.format(currSensorState))
            self.barrierLastInputState = currSensorState
            if currSensorState == 0:
                Delay.once(self.barrierClosedDelay, self.onBarrierClosed)

    def onBarrierClosed(self):
        log.info('Barrier closed')
        try:
            queue_number = self.barrierQueue.get(block=False)
            log.info('Get queue number {} from BarrierQueue'.format(queue_number))
            self.openBarrier(queue_number)
        except Empty:
            try:
                self.barrierSemaphore.release()
            except ValueError:
                return

    def enableMoneyReceive(self):
        print " Enable Money Receive"
        log.info('Enable Money Receive')
        self.billAcceptor.inhibitOff()
            # self._rplc.getModules()[1].inhibit(False)

    def disableMoneyReceive(self):
        print " Disable Money Receive"
        log.info('Disable Money Receive')
        self.billAcceptor.inhibitOn()
            # self._rplc.getModules()[1].inhibit(True)

    def enableCardsReceive(self):
        print " Enable Card Receive"
        log.info('Enable Card Receive')
        if not self.acquiring_emulate:
            self._bacq.beginReadCardUIDScenario()

    def disableCarsdReceive(self):
        print " Disable Card Receive"
        log.info('Disable Card Receive')
        if not self.acquiring_emulate:
            self._bacq.cancelScenario()

    def saleHandler(self):
        print "sale handler"
        if not self.acquiring_emulate:
            self._bacq.beginSaleScenario(self.operationScenario.getSpendingSum() * 100)

    def getKkmGetStatusFiscalization(self):
        """Фискализирован ли казначей?"""
        if not self._atol_disabled:
            try:
                return self.kkm.getStatusFiscalization()
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))

    def kkmFiscalPaymentRobot(self, typeClose=Atol.KKM_TYPE_CLOSE_1, printFiscalCheck=True,
                              printNonFiscalCheck=True):
        'Формирование фискального чека и не фискального для БК и нала при оплате робота'
        'Программа какая всегда печатается, + услуги'
        listPositions = [
            {
                "quantity": 1,
                "price": self.operationScenario.getProgramPrice(),
                "summ": self.operationScenario.getProgramPrice(),
                "check_text": (u"Мойка на роботе №"+
                               str(self.operationScenario.getRobotNumber()) +
                               u" по программе " +
                               self.operationScenario.getProgramName())
            }
        ]
        'Добавлем позиции в фискальный чек'
        servicesMask = self.operationScenario.getServicesMask()
        for s in self.utilityManager.getUtilities('service'):
            if servicesMask & (1 << s.getIndex()):
                listPositions.append({
                    "quantity": 1,
                    "price": s.getPrice(),
                    "summ": s.getPrice(),
                    "check_text": u'Опция: {}'.format(
                        s.getCaption().replace('<br>', ' ').replace('  ', ' '))
                })

        try:
            if not self._atol_disabled and printFiscalCheck:
                self.kkm.paymentListPosition(
                    listPositions=listPositions,
                    wantPrint=self.operationScenario.getWantPrintCheck(),
                    type_close=typeClose,
                    type_nds=self.atol_nds_type,
                    type_sno=self.atol_type_sno
                )
        except AtolCommandException as e:
            log.error(u'{0}: {1}'.format(e.message, e.operationResult))

        'Нефискальный чек'
        lines = []
        lines.append(u'РоботКарВош')
        lines.append(u'Мойка на роботе: {}'.format(self.operationScenario.getRobotNumber()))
        lines.append(u'По программе: {}'.format(self.operationScenario.getProgramName()))
        lines.append(u'Номер очереди: {}'.format(
            self.robotController[self.operationScenario.getRobotNumber() - 1].queueNumber
        ))
        lines.append(u'Стоимость программы: {}'.format(self.operationScenario.getProgramPrice()))
        lines.append(u'Время: {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        if printFiscalCheck and not self._atol_disabled:
            try:
                if self.isKkmFiscal:
                    lines.append(u'Номер ФД: {}'.format(str(self.kkm.getLastReceiptQRData()['i'])))
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))
        lines.append(self.operationScenario.getPayDescription())

        servicesMask = self.operationScenario.getServicesMask()

        for s in self.utilityManager.getUtilities('service'):
            if servicesMask & (1 << s.getIndex()):
                lines.append(u'Использована опция: {}, Цена: {} '.format(
                    s.getCaption().replace('<br>', ' ').replace('  ', ' '),
                    s.getPrice()))
        for l in lines:
            print(l)
            log.info(u"check:" + l)
        'Add selected services to check lines'
        if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                self.atolEnabled and
                self.printServiceCheckEnabled and
                self.operationScenario.getHasPaper()):
            try:
                self.kkm.printNonFiscalCheckMultiline(lines)
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))

    @connection_manager.autoConnect
    def processPayment(self):
        'PAY DESTINATION'
        if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_FILL:
            'calculate cashback'
            cardBalance = self.operationScenario.getCardBalance()
            moneyInserted = self.operationScenario.getMoneyInserted()
            cashBack = 0
            for i in range(len(self.client_card_cash_back_level)):
                if (self.client_card_cash_back_border[i] <= cardBalance):
                    cashBack = self.client_card_cash_back_level[i]

            moneyWithCashBack = moneyInserted + moneyInserted * cashBack / 100
            moneyFromCashback = moneyInserted * cashBack / 100
            self.operationScenario.setMoneyFromCashback(moneyFromCashback)
            lines = []
            lines.append(u'РоботКарВош')
            lines.append(u'Пополнение клиентской карты: {}'.format(self.operationScenario.getCardUid()))
            lines.append(u'Начальный баланс: {}'.format(cardBalance))
            lines.append(u'Величина пополнения: {}'.format(moneyInserted))
            lines.append(u'Величина КЭШБЭКА: {}%'.format(cashBack))
            lines.append(u'')
            lines.append(u'Сумма на карте после пополнения: {}'.format(cardBalance + moneyWithCashBack))

            'Add selected services to check lines'
            if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                    self.atolEnabled and
                    self.operationScenario.getHasPaper()):
                try:
                    self.kkm.printNonFiscalCheckMultiline(lines)
                except AtolCommandException as e:
                    log.error(u'{0}: {1}'.format(e.message, e.operationResult))

            'Update database'
            # пополнение клиентсвой карты

            card = self.operationScenario.getClientCard()
            card.refill(moneyWithCashBack)

        elif self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_CARD_BUY:
            'Sell card'
            if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                    self.operationScenario.getWantPrintCheck() and
                    self.atolEnabled):
                try:
                    self.kkm.printNonFiscalCheck(u'РоботКарВош', \
                                                 u'', \
                                                 self.operationScenario.getPayDescription(), \
                                                 self.operationScenario.getSpendingSum() \
                                                 )
                except AtolCommandException as e:
                    log.error(u'{0}: {1}'.format(e.message, e.operationResult))
            if self.cardDispenser is not None:
                log.info('Dispense client card')
                try:
                    self.cardDispenser.dispense()
                except CardDispenserException:
                    log.error('Error dispensing client card')

                    lines = []
                    lines.append(u'РоботКарВош')
                    lines.append(u'')
                    lines.append(u'Сбой выдачи карты')
                    lines.append(u'Обратитесь к администратору мойки')

                    if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                            self.atolEnabled and
                            self.operationScenario.getHasPaper()):
                        try:
                            self.kkm.printNonFiscalCheckMultiline(lines)
                        except AtolCommandException as e:
                            log.error(u'{0}: {1}'.format(e.message, e.operationResult))

        elif self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
            log.info("Selected robot: {}".format(self.operationScenario.getRobotNumber()))
            programNumber = self.operationScenario.getProgramNumber()
            attribute = 0
            paidProgram = self.utilityManager.getUtility('program', programNumber)
            if (not self.sideGateDisabled) and (not self.sideGateEmulate):
                if (not paidProgram.hasOptions() or
                        self.dryZoneDisabled or self.service_night_disabled):
                    attribute = 1
            rb_idx = self.operationScenario.getRobotNumber() - 1
            p_type = db.ProgramType.get(db.ProgramType.name == 'program')
            program = db.Program.get((db.Program.name == paidProgram.getCaption()) &
                                     (db.Program.program_type == p_type))
            s_type = db.ProgramType.get(db.ProgramType.name == 'service')
            services = []
            for i, price in enumerate(self.operationScenario.getServiceSelected()):
                u = self.utilityManager.getUtility('service', i)
                if int(price) > 0:
                    services.append(db.Program.get((db.Program.name == u.getCaption()) &
                                                   (db.Program.program_type == s_type)))

            queueNumber = self.robotController[rb_idx]\
                .requestToEnter(program=program, services=services, attribute=attribute)
            self.operationScenario.updateQueue(queueNumber)
            if self.barrierEnabled is True:
                log.info('Barrier will be opened after {} seconds.'
                         .format(self.barrierInviteDelay))
                Delay.once(self.barrierInviteDelay,
                           self.openBarrierOrPutIntoQueue,
                           queueNumber)
        elif self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_CLIENT_MANUAL_WASH:
            lines = []
            lines.append(u'РоботКарВош')
            lines.append(u'Ручная мойка')
            lines.append(u'Стоимость ручной мойки: {}'.format(self.operationScenario.getSpendingSum()))

            if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                    self.atolEnabled and
                    self.operationScenario.getHasPaper()):
                try:
                    self.kkm.printNonFiscalCheckMultiline(lines)
                except AtolCommandException as e:
                    log.error(u'{0}: {1}'.format(e.message, e.operationResult))

        dispenseError, billsDispensed, billsNotDispensed = self.operationScenario.getBillDispenseResult()

        if dispenseError:
            lines = []
            lines.append(u'Ошибка выдачи сдачи')
            lines.append(u'Обратитесь к администратору мойки')
            lines.append(u'')
            lines.append(u'')
            lines.append(u'Количество выданных купюр: {}'.format(billsDispensed))
            lines.append(u'Количество задержанных купюр: {}'.format(billsNotDispensed))

            if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                    self.atolEnabled and
                    self.operationScenario.getHasPaper()):
                try:
                    self.kkm.printNonFiscalCheckMultiline(lines)
                except AtolCommandException as e:
                    log.error(u'{0}: {1}'.format(e.message, e.operationResult))

        'PAY SOURCE'
        if (self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD) or \
                (self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_QR_CODE):
            log.info('Bank Payment %s rubles for: %s.', \
                         self.operationScenario.getSpendingSum(), \
                         self.operationScenario.getPayDescription() \
                         )
            if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                self.kkmFiscalPaymentRobot()
            else:
                try:
                    if not self._atol_disabled:
                        if self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD:
                            self.kkm.paymentListPosition(
                                listPositions=[{
                                    "quantity": 1,
                                    "price": self.operationScenario.getSpendingSum(),
                                    "summ": self.operationScenario.getSpendingSum(),
                                    "check_text": self.operationScenario.getPayDescription()
                                }],
                                wantPrint=self.operationScenario.getWantPrintCheck(),
                                type_close=Atol.KKM_TYPE_CLOSE_1,
                                type_nds=self.atol_nds_type,
                                type_sno=self.atol_type_sno
                            )
                        else:
                            self.kkm.paymentListPosition(
                                listPositions=[{
                                    "quantity": 1,
                                    "price": self.operationScenario.getSpendingSum(),
                                    "summ": self.operationScenario.getSpendingSum(),
                                    "check_text": self.operationScenario.getPayDescription()
                                }],
                                wantPrint=self.operationScenario.getWantPrintCheck(),
                                type_close=Atol.KKM_TYPE_CLOSE_2,
                                type_nds=self.atol_nds_type,
                                type_sno=self.atol_type_sno
                            )
                except AtolCommandException as e:
                    log.error(u'{0}: {1}'.format(e.message, e.operationResult))

        # оплата наличкой (печать чека)
        elif self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_CASH:
            log.info('Cash Payment %s rubles for: %s. Price: %s. Check wanted: %s', \
                         self.operationScenario.getMoneyInserted(), \
                         self.operationScenario.getPayDescription(), \
                         self.operationScenario.getSpendingSum(), \
                         str(self.operationScenario.getWantPrintCheck()))
            if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                self.kkmFiscalPaymentRobot(typeClose=Atol.KKM_TYPE_CLOSE_CASH)
            else:
                try:
                    if not self._atol_disabled:
                        self.kkm.paymentListPosition(
                            # summ НЕ используется в self.kkm.paymentListPosition, но
                            # т.к. quantity = 1, значит price == summ, поэтому
                            # в price передаётся getMoneyInserted, иначе будет ошибка
                            listPositions=[{
                                "quantity": 1,
                                "price": self.operationScenario.getMoneyInserted(),
                                "summ": self.operationScenario.getMoneyInserted(),
                                "check_text": self.operationScenario.getPayDescription()
                            }],
                            wantPrint=self.operationScenario.getWantPrintCheck(),
                            type_close=Atol.KKM_TYPE_CLOSE_CASH,
                            type_nds=self.atol_nds_type,
                            type_sno=self.atol_type_sno
                        )
                except AtolCommandException as e:
                    log.error(u'{0}: {1}'.format(e.message, e.operationResult))


        # оплата клиентской картой
        elif self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_CLIENT_CARD:
            log.info('Client Card Payment %s rubles for: %s.', \
                         self.operationScenario.getMoneyInserted(), \
                         self.operationScenario.getPayDescription() \
                         )
            card = self.operationScenario.getClientCard()
            card.spend(self.operationScenario.getSpendingSum())
            if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                self.kkmFiscalPaymentRobot(printFiscalCheck=False)
        # Оплата чего либо: реалом (банк. картой, налом), виртуалом (клиентской картой)
        paySource = self.operationScenario.getPaySource()
        if paySource == OperationScenario.PAY_SOURCE_BANK_CARD:
            transaction = FinanceTransaction.MoneyTransaction(FinanceTransaction.SOURCE_TYPE.BANK_CARD)
        elif paySource == OperationScenario.PAY_SOURCE_CASH:
            transaction = FinanceTransaction.MoneyTransaction(FinanceTransaction.SOURCE_TYPE.CASH)
        elif paySource == OperationScenario.PAY_SOURCE_CLIENT_CARD:
            transaction = FinanceTransaction.CardTransaction(FinanceTransaction.SOURCE_TYPE.CLIENT_CARD)
            transaction.setSourceCard(self.operationScenario.getClientCard())
        elif paySource == OperationScenario.PAY_SOURCE_QR_CODE:
            transaction = FinanceTransaction.MoneyTransaction(FinanceTransaction.SOURCE_TYPE.QR_CODE)
        else:
            transaction = None
            log.critical(u"Неизвестный тип транзакции. Доступные методы: реал, виртуал")

        sourceInstallation = Installation.Terminal(1)

        # Источние платежа. У проекта терешко пока только 1 терминал
        transaction.setSourceInstallation(sourceInstallation)
        log.info('Set destination type in type payment.')
        # Чего происходит покупка?
        payDest = self.operationScenario.getPayDestination()
        if payDest == OperationScenario.PAY_DEST_CLIENT_CARD_BUY:
            transaction.setDestinationInstallation(sourceInstallation)
            transaction.bayCard(self.operationScenario.getSpendingSum())

        elif payDest == OperationScenario.PAY_DEST_ROBOT:
            # Целевое оборудование: робот. (оплата мойки робота) . Если есть.
            destRobotId = self.operationScenario.getRobotNumber()
            if destRobotId:
                transaction.setDestinationInstallation(Installation.Robot(destRobotId))
            transaction.bayWorkTimeInstallation(self.operationScenario.getSpendingSum(), 0)
            db.FinancePriceArchive.create(id=uuid(),
                                          finance=transaction.id,
                                          price=self.operationScenario.getProgramPrice(),
                                          program_name=self.operationScenario.getProgramName(),
                                          program_type_name='program')
            selectedService = self.operationScenario.getServiceSelected()
            self.operationScenario.setServiceSelected([])
            for i, price in enumerate(selectedService):
                u = self.utilityManager.getUtility('service', i)
                if int(price) > 0:
                    db.FinancePriceArchive.create(id=uuid(),
                                                  finance=transaction.id,
                                                  price=price,
                                                  program_name=u.getCaption(),
                                                  program_type_name='service')
            # сохраняем financeID для очереди
            self.robotController[self.operationScenario.getRobotNumber() - 1].setFinance(transaction.id)

        elif payDest == OperationScenario.PAY_DEST_CLIENT_CARD_FILL:
            transaction.setDestinationInstallation(sourceInstallation)
            transaction.setDestinationCard(self.operationScenario.getClientCard())
            transaction.refillCard(self.operationScenario.getSpendingSum(),
                                   self.operationScenario.getMoneyFromCashback())

        log.info("Payment sendied to data storage.")
        if payDest != OperationScenario.PAY_DEST_CLIENT_MANUAL_WASH:
            bd = FinanceTransaction.BillsDispensed()
            bd.addBills(billsDispensed, 50)
            bd.save(transaction._financeID)
        else:
            log.info("Manual wash is not happend")

    def isRobotAllowed(self, robotIndex):
        good = self.robotController[robotIndex].isGood()
        return good

    def enquireCardDispenserHandler(self):
        empty, lack, full, fail = (False, False, False, True)
        tries = 0
        if self.cardDispenser is not None:
            for tries in range(3):
                #wStat, sStat = self.crt541.enquiпry()
                currTime = time.time()
                status = self.cardDispenser.getStatus()
                print "Worked time  enquireCardDispenserHandler %s" % (time.time() - currTime)
                log.info("Card dispenser status: {}".format(str(status)))
                if status is None:
                    continue
                empty = status.isStackEmpty()
                lack = status.isStackLack()
                full = (not empty) and (not lack)
                fail = status.isFail()
                if fail is True:
                    log.warning("Card dispenser failed.")
                    self.cardDispenser.reset()
                    time.sleep(1)
                else:
                    break
        return empty, lack, full, fail

    def billDispenserFailedHandler(self):
        """Опрос купюрника на то можно ли выдать сдачу или нет."""
        if self.billDispenser is None:
            "Может вызваться, если купюрник в режиме эмуляции"
            log.warning("Bill dispenser in mode emulated. Return stub value as bill dispenser fail.")
            return True

        responser = self.billDispenser.getStatus()
        print(u"Диспенсер может выдавать сдачу? %s " % u"Нет" if responser else u"Да")
        return responser

    def dispenseBillHandler(self, count, callbackDispenseIsSuccess=None):
        log.info('Dispense %s bills', count)
        dispenseError, billsDispensed = self.billDispenser.dispense(count, callbackDispenseIsSuccess)
        self.operationScenario.setBillDispenseResult(dispenseError,
                                                         billsDispensed,
                                                         count - billsDispensed)

    def getAvailableChange(self):
        return self.billDispenser.getAvailableChangeBillCount()*self._dispenseBill

    def getAvailableChangeBills(self):
        return self.billDispenser.getAvailableChangeBillCount()

    def onBill(self, bill, event, *args, **kwargs):
        ''' bill inserted handler '''
        if event is BillAcceptorInterface.ESCROW_POSITION:
            log.info("Bill {} in escrow position".format(bill))
            ''' this callback can be called before operationScenario object was
             created in case of bill was in escrow position and power was
             switched off. After switching on the first message in poll queue is
             "bill in escrow position". So we just return it to the customer by
             default.
            '''
            if hasattr(self, 'operationScenario'):
                self.billAcceptor.reject(not self.operationScenario.isBillAllowed(bill))
            else:
                self.billAcceptor.reject(True)
        elif event is BillAcceptorInterface.STACKED:
            log.info("Bill {} stacked".format(bill))
            self.operationScenario.updateMoneyInserted(bill)

    def onErrorBillAcceptor(self, message=u"Неизвестная ошибка купюроприемника"):
        self.pageErrorBillAcceptor.show(
            error_text=message
        )

    def onBillBusy(self, state):
        ' same as on bill behaviour '
        if hasattr(self, 'operationScenario'):
            self.operationScenario.enableButtons(not state.isBillAcceptorBusy())

    def processClientCard(self):
        """
        Точка входа при поднесении карты.

        Установки OperationScenario
        -uid
        -тип карты как "клиентская"
        -ее подтип, взятой из базы данных
        -баланс

        Если карты нет, то создать ее
        """
        self.operationScenario.setCardType(OperationScenario.CARD_TYPE_MIFARE)

        if not self._acquiring_client_card_disabled:
            self.uid_bint = int(self._card_data[0],16)
            self.operationScenario.setCardUid(self.uid_bint)

            card = Card.Card(self.uid_bint)
            self.operationScenario.setClientCard(card)
            # Зависит от настройки card_auto_create.
            # TODO сделать каллбэк для создания новой карты. Чтобы хоть как-то отслеживать новую карту.
            # if not cardExists:
            #     logging.info('(' + __name__ + ')New card %s was created', self.uid_bint)
            #     self._db.card_insert(self.uid_bint)
            #     self.operationScenario.setCardType(OperationScenario.CARD_TYPE_MIFARE_NEW)
            #     self.operationScenario.setNextPage("PageMifareNew")
            #     self.operationScenario.setCardBalance(0)
            log.info('Existing card %s with %s rubles', card.uid, card.balance)
            self.operationScenario.setCardBalance(card.balance)
            self.operationScenario.setCardSubType(card.type)
            self.operationScenario.setCardName(card.card_name)
            self.operationScenario.setClientName(card.client_name)
            self.operationScenario.cardEvent()

    def processBankCard(self):
        self.operationScenario.setCardType(OperationScenario.CARD_TYPE_BANK)
        # self.operationScenario.cardEvent()

    def acquiringError(self, message):
        if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                self.atolEnabled and
                self.operationScenario.getHasPaper()):
            try:
                self.kkm.printError(message)
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))
        self.operationScenario.setCardInError(True)
        self.pageError.show(error_text=message)
        if not self.acquiring_emulate:
            self._bacq.cancelScenario()

    # опути меня, ханлер ><
    def bankacquiringHanler(self, message_code, message_data):
        if message_code == BankAcquiring.UID:
            self._card_data = message_data

        elif (message_code == BankAcquiring.CARD_OUT) and not self.operationScenario.getCardInError():
            if self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD:
                log.info('ACQUIRING CardOut: Bank')
                # self.processBankCard()
            elif (self._card_data[1].strip() == 'Mifare'):
                log.info('ACQUIRING CardOut: Client')
                self.processClientCard()

        elif message_code == BankAcquiring.PRINT_LINE:
            line = message_data
            if (not self.operationScenario.atolModeOnlyQrCodeCheck() and
                    self.atolEnabled and
                    self.operationScenario.getHasPaper() and
                    self.print_sleep_check):
                if not self.kkm.isPrinterFailed():
                    try:
                        if line[1] == 0:
                            if self._start_sleep_check == True:
                                log.info('ACQUIRING Start printing sleep check...')
                                self.kkm.printLine(u'БАНКОВСКИЙ ЧЕК', Atol.TextWrapNone, Atol.AlignmentCenter)
                                self.kkm.printLine(u' ', Atol.TextWrapNone, Atol.AlignmentLeft)
                                self.kkm.printLine(u' ', Atol.TextWrapNone, Atol.AlignmentLeft)
                                self.kkm.printLine(u' ', Atol.TextWrapNone, Atol.AlignmentLeft)
                                self._start_sleep_check = False

                            self.kkm.printLine(line[0], Atol.TextWrapNone, Atol.AlignmentLeft)
                        else:
                            log.info('ACQUIRING End printing sleep check...')
                            self._start_sleep_check = True
                            self.kkm.printLine(line[0], Atol.TextWrapNone, Atol.AlignmentLeft)
                            self.kkm.printEnd()
                    except AtolCommandException as e:
                        log.error(u'{0}: {1}'.format(e.message, e.operationResult))

        elif message_code == BankAcquiring.INSERT_CARD:
            self.operationScenario.setCardInError(False)
            self._bacq.beginReadCardUIDScenario()
            log.info('ACQUIRING transaction initialized')

        elif message_code == BankAcquiring.CARD_IN:
            log.info('ACQUIRING card in')

        elif message_code == BankAcquiring.PIN_REQUIRED:
            log.info('ACQUIRING pin required')
            self.be.switchPageByName("PageBankPincode")
            self.operationScenario.clearPincodeMask()

        elif message_code == BankAcquiring.PIN_NUM:
            log.info('ACQUIRING pin num')
            self.operationScenario.pushPincodeMask()
            self.operationScenario.updatePincodeMask()

        elif message_code == BankAcquiring.PIN_ENTER:
            log.info('ACQUIRING pin enter')
            self.pageBankExchange.show()

        elif message_code == BankAcquiring.PIN_CLEAR:
            log.info('ACQUIRING pin clear')
            self.operationScenario.popPincodeMask()
            self.operationScenario.updatePincodeMask()

        elif message_code == BankAcquiring.ONLINE_REQUIRED:
            log.info('ACQUIRING Auth online required')
            self.pageBankExchange.show()

        elif message_code == BankAcquiring.AUTH_FAIL:
            log.error('ACQUIRING auth fail %s', message_data)
            message = unicode(message_data, "utf-8")
            self.acquiringError(message)

        elif message_code == BankAcquiring.ERROR:
            log.error('ACQUIRING error %s', message_data)
            self.acquiringError(unicode(message_data, "utf-8"))

        elif message_code == BankAcquiring.SOFTWARE_ERROR:
            log.error('ACQUIRING Software error %s', message_data)
            self.acquiringError(unicode(message_data, "utf-8"))

        elif message_code == BankAcquiring.AUTH_SUCCESS:
            log.info('ACQUIRING Auth Success')
            self.operationScenario.setMoneyInserted(self.operationScenario.getSpendingSum())
            self.operationScenario.checkProcessing()
            # self.be.switchPageByName("PageWantPrint")
            # self.processPayment()
            # self._bacq.cancelScenario()

    # Отчеты для юрлиц
    def createCompanyCard(self, description):
        log.info("Company create for uid %s", self.operationScenario.getCardUid())
        self.companyReports.cardChangeCompany(self.operationScenario.getCardUid(), description)
        self.companyReports.createReportByCard(self.operationScenario.getCardUid(), "0")

    def getAllCompanyCard(self):
        log.info("Get all from card info")
        return self.companyReports.getAllCompanyCard()

    def getReportsByCard(self):
        log.info("Get reports by card")
        return self.companyReports.getReportsByCard(self.operationScenario.getCardUid())

    def getReportsClient(self):
        log.info("Get reports by client")
        return self.companyReports.getReportsByClient(self.operationScenario.getClientIdForReports())

    def createReportByCard(self):
        log.info("Create report by card")
        # self._db.createReportByCard(self.operationScenario.getCardUid())
        self.companyReports.createReportByCard(self.operationScenario.getCardUid())

    def createReportByClientId(self):
            self.companyReports.createReportByClientId(self.operationScenario.getClientIdForReports())

    def sendCompanyReportToEmail(self, reportID, easy=False, normal=False):
        log.info("Sending company report...")

        # настройки email
        sender = config.getProperty('email_sender')
        pwd = config.getProperty('email_pwd')
        receivers = config.getProperty('email_receivers_company_reports', default='["subondarkness@gmail.com"]', _type="json")
        serv = config.getProperty('email_server')

        emailNotifier = EmailNotifier(sender, receivers, serv, sender, pwd)
        if easy:
            env = Environment(
                loader=PackageLoader(__name__, 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
            )
            template = env.get_template('_easy_company_report.jinja2')

            dtr = datetime.datetime.now()
            report = self.companyReports.getReportById(reportID)
            card = Card.Card(self.operationScenario.getCardUid())
            data = {
                "reportID": reportID,
                "dateSendedReport": dtr.strftime("%d.%m.%Y %H:%M"),
                "report": report,
                "card": card
            }
            rendered = template.render(**data)
            pdfkit.from_string(rendered, './companyReport.pdf')
            emailNotifier.notifyFile('./companyReport.pdf',
                                     "Отчет компании по '%s'" % report.account.client.description.encode("utf8"),
                                     "%s %s.%s" % ("report",
                                                   str(time.asctime()),
                                                   'companyReport.pdf'
                                                   ))

    def checkInternet(self):
        try:
            urllib2.urlopen('http://216.58.192.142', timeout=1)
            return True
        except urllib2.URLError as err:
            return False

    def getLastCheckQRCode(self):
        """Получить qr код последнего чека Pillow изображение"""
        if self.drawTestQrCodeEnabled or self._atol_disabled:
            log.warning("Warning! It test QR code!")
            return 'iVBORw0KGgoAAAANSUhEUgAAAUoAAAFKAQAAAABTUiuoAAAB5klEQVR4nO2aTWrkMBSE640Ms7Qh' \
                   'B+ijyDfrq0lHmQME5GVApmYhye0kDOMO2K1FvZVsf4sC8f5txEGLv46SgFChQoUKFXomatUGIJoZ' \
                   'sAwAlvZ6Pl2A0GdQT5JMADwzbAZgMxxJkp/RcwQIfQZdmgtFG8CA1RgAFH+7QoDQH6B2TwDiLb9K' \
                   'gNDnUEe7J0ebXyVA6L+sxbmRABaAcXIglrfiXPve+eVahVY0mpnZVCOhzeXtWkrCKwQIPWLFtx4u' \
                   'xC1l8bNndaBVaOu3JuxbrTittvtwvgChx4ybAWMGfHJkaB/KI0kyvFyr0O1S2mMYWyRkAkjm2jvr' \
                   'tjpCHUlm2P3PgN0EI05Os4xu0FZlLKsRyxsRJ5cBrAOBx+k8AUKfj4QlZbHmrRIYPTMYoLzVD7rP' \
                   'Wz45AmOd7zJsjPJWh2i8ZcCnOn63e/OtywQI/Y9tE3aXDctQ68F4+zBEAwxYNcvoBt31W60SbFst' \
                   '/wiRioQ9obvdcX0cUBfIo7aR3aG73XFarZyw9cnhfAFCD9mXmpBhzHWC8TBFwn5RRzP7zdpqpesF' \
                   'CD2M+oTyXwY8PwzxprzVD/p1d2w+AIbxfTCM7xcIEPqDyVOxrRMeyTJ52mp55a0O0G+74/2pXp6m' \
                   'ukKFChUqtBf0L3hwMjWXoUqjAAAAAElFTkSuQmCC'
        else:
            try:
                img = self.kkm.getQRCode(self.kkm.getQRDataString(self.kkm.getLastReceiptQRData()))
                buffer = cStringIO.StringIO()
                img.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue())
                return img_str
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))

    def getThankQRCode(self):
        if self.drawTestQrCodeEnabled or self._atol_disabled:
            log.warning("Warning! It test QR code!")
            return 'iVBORw0KGgoAAAANSUhEUgAAAUoAAAFKAQAAAABTUiuoAAAB5klEQVR4nO2aTWrkMBSE640Ms7Qh' \
                   'B+ijyDfrq0lHmQME5GVApmYhye0kDOMO2K1FvZVsf4sC8f5txEGLv46SgFChQoUKFXomatUGIJoZ' \
                   'sAwAlvZ6Pl2A0GdQT5JMADwzbAZgMxxJkp/RcwQIfQZdmgtFG8CA1RgAFH+7QoDQH6B2TwDiLb9K' \
                   'gNDnUEe7J0ebXyVA6L+sxbmRABaAcXIglrfiXPve+eVahVY0mpnZVCOhzeXtWkrCKwQIPWLFtx4u' \
                   'xC1l8bNndaBVaOu3JuxbrTittvtwvgChx4ybAWMGfHJkaB/KI0kyvFyr0O1S2mMYWyRkAkjm2jvr' \
                   'tjpCHUlm2P3PgN0EI05Os4xu0FZlLKsRyxsRJ5cBrAOBx+k8AUKfj4QlZbHmrRIYPTMYoLzVD7rP' \
                   'Wz45AmOd7zJsjPJWh2i8ZcCnOn63e/OtywQI/Y9tE3aXDctQ68F4+zBEAwxYNcvoBt31W60SbFst' \
                   '/wiRioQ9obvdcX0cUBfIo7aR3aG73XFarZyw9cnhfAFCD9mXmpBhzHWC8TBFwn5RRzP7zdpqpesF' \
                   'CD2M+oTyXwY8PwzxprzVD/p1d2w+AIbxfTCM7xcIEPqDyVOxrRMeyTJ52mp55a0O0G+74/2pXp6m' \
                   'ukKFChUqtBf0L3hwMjWXoUqjAAAAAElFTkSuQmCC'
        else:
            try:
                img = self.kkm.getQRCode("Thank you for payment!")
                buffer = cStringIO.StringIO()
                img.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue())
                return img_str
            except AtolCommandException as e:
                log.error(u'{0}: {1}'.format(e.message, e.operationResult))

    def _syncProgramCountDb(self, controller, mode = RobotController.MODE_SYNC_SET):
        robot = Installation.Robot(controller.getRobotNumber())
        if mode == RobotController.MODE_SYNC_SET:
            robot.updateProgramStatistics(controller)
        elif mode == RobotController.MODE_SYNC_GET:
            controller.updateProgramStatistics(robot)

    def checkHasPaper(self):
        try:
            if self.kkm is not None:
                return self.kkm.checkPrinter() != PrinterStatus.PAPER_OUT
            else:
                return False
        except AtolCommandException as e:
            log.error(u'{0}: {1}'.format(e.message, e.operationResult))

    def getReportsCountFromBuffer(self):
        """При вызове, обработать AtolCommandException!"""
        return self.kkm.getReportsCountFromBuffer()

    @connection_manager.autoConnect
    def onCodeReadHandler(self, hash, *args, **kwargs):
        log.info(u'QR Order hash: {}'.format(hash))
        if 'reader_number' in kwargs:
            reader_number = kwargs['reader_number']
            if self.operationScenario.isQrReaderLocked(reader_number):
                log.warning(u'QR Reader{} locked! QR Order '
                            u'cannot be processed!'.format(reader_number + 1))
                return
        try:
            dbOrder = db.ClientOrder.get(db.ClientOrder.hash == hash)
            order = QrOrder(dbOrder, self.priceCalendar)
        except db.ClientOrder.DoesNotExist:
            log.error(u'QR Order not found!')
            return
        else:
            if order.isPaid():
                log.info('Handle QR Order: {}'.format(order.getId()))
                self.handleDifferentReaderNumberCase(order, reader_number)
                successfully = self.handleServiceUnavailableCase(order)
                if successfully:
                    successfully = self.handleOrderPriceDifferenceCase(order)
                    if successfully:
                        self.handleRobotUnavailableCase(order)
            else:
                log.error('QR Order failed! QR Order has been done or canceled!')
                self.sendNotification(title=Vmachine.FCM_TEXT['FAILED_TO_USE_QR'],
                                      body=Vmachine.FCM_TEXT['DONE_OR_CANCELED'],
                                      order=order)

    def handleDifferentReaderNumberCase(self, order, currReader):
        log.info('Handle Different Reader Number Case')
        currRobot = order.getRobotNumber()
        if (currRobot - 1) != currReader:
            changedRobot = currReader + 1
            log.warning('Change robot number in order: {} -> {}.'
                        .format(currRobot, changedRobot))
            order.setRobotNumber(changedRobot)

    def handleServiceUnavailableCase(self, order, *args, **kwargs):
        log.info('Handle Service Unavailable Case')
        if order.containsAnyService():
            if self.dryZoneDisabled or order.containsAnyUnavailableService():
                log.warning('QR Order failed! '
                            'Dry zone disabled or services unavailable!')
                self.sendNotification(title=Vmachine.FCM_TEXT['FAILED_TO_USE_QR'],
                                      body=Vmachine.FCM_TEXT['SERVICE_UNAVAILABLE'],
                                      order=order)
                return False
        return True

    def handleOrderPriceDifferenceCase(self, order):
        log.info('Handle Order Price Difference Case')
        diff = order.getOrderPriceDifference()
        if diff < 0:
            log.error(u'QR Order failed! Order price < current price by {}₽'
                      .format(diff))
            self.sendNotification(title=Vmachine.FCM_TEXT['FAILED_TO_USE_QR'],
                                  body=Vmachine.FCM_TEXT['PRICE_LESS'],
                                  order=order)
            return False
        else:
            if diff > 0:
                log.info(u'QR Order price > current price by {}₽'.format(diff))
                self.refundOverpaidCostToCard(order=order, amount=diff)
                self.sendNotificationDelayed(delay=60,
                                             title=Vmachine.FCM_TEXT['BONUSES_ACCRUED'] + str(diff),
                                             body=Vmachine.FCM_TEXT['PRICE_MORE'],
                                             order=order)
            return True

    def handleRobotUnavailableCase(self, order):
        log.info('Handle Robot Unavailable Case')
        robot = order.getRobotNumber()
        allowed = self.isRobotAllowed(robot - 1)
        maintenance = self.operationScenario.getRobotMaintenance(robot - 1)
        if (allowed is True) and (maintenance == 0):
            self.putIntoRobotsQueue(order)
            order.done()
            log.info('QR Order successfully done!')
        else:
            log.warning('QR Order failed! Robot{} unavailable'.format(robot))
            self.sendNotification(title=Vmachine.FCM_TEXT['FAILED_TO_USE_QR'],
                                  body=Vmachine.FCM_TEXT['ROBOT_UNAVAILABLE'],
                                  order=order)

    def putIntoRobotsQueue(self, order):
        log.info('Put QR Order Into Robots Queue')
        robot = order.getRobotNumber()
        prog_num = order.getProgramNumber()
        attribute = 0
        paidProgram = self.utilityManager.getUtility('program', prog_num)
        if (not self.sideGateDisabled) and (not self.sideGateEmulate):
            if (not paidProgram.hasOptions() or
                    self.dryZoneDisabled or self.service_night_disabled):
                attribute = 1
        q = self.robotController[robot - 1].requestToEnter(
            program=order.getPrograms()[0], services=order.getServices(),
            attribute=attribute)
        self.operationScenario.updateQueue(q)
        log.info(u'[QR ORDER] RobotCarWash')
        log.info(u'[QR ORDER] Мойка на роботе: {}'.format(robot))
        program = order.getOrderPrograms()[0]
        log.info(u'[QR ORDER] По программе: {}'.format(program.name))
        services = order.getOrderServices()
        for service in services:
            desc = service.description.replace('<br>', ' ').replace('  ', ' ')
            price = order.getCurrentProgramPrice(service)
            log.info(u'[QR ORDER] Использована опция: {}; '
                     u'Цена: {}₽'.format(desc, price))
        log.info(u'[QR ORDER] Номер очереди: {}'.format(q))
        log.info(u'[QR ORDER] Сумма заказа: {}₽'.format(order.getTotalPrice()))
        log.info(u'[QR ORDER] Время оплаты: {}'.format(order.getDate()))
        self.sendNotification(title=Vmachine.FCM_TEXT['QR_USED'],
                              body=Vmachine.FCM_TEXT['QUEUE_NUMBER'] + str(q),
                              order=order)

    def sendNotification(self, title, body, order):
        order_id = order.getId()
        token = Card.Card(order.getCard().uid).getProperty('firebase_token')
        log.info(u'Send notification')
        log.info(u' '.join([u'title:', title]))
        log.info(u' '.join([u'body:', body]))
        log.info(u' '.join([u'order_id:', order_id]))
        try:
            r = requests.post(url=self.firebase_url + '/send', json={
                'title': title,
                'body': body,
                'token': token,
                'order_id': order_id
            })
            if r.status_code == requests.codes.ok:
                log.info(u' '.join([u'Notification sent:', r.text]))
            else:
                log.error(u' '.join([u'Failed to send notification:', r.text]))
        except Exception as e:
            log.error(u' '.join([u'Failed to send notification:', str(e)]))

    def sendNotificationDelayed(self, delay, *args, **kwargs):
        Delay().once(delay, self.sendNotification, **kwargs)

    def refundOverpaidCostToCard(self, order, amount):
        try:
            url = self.robotcarwashrest_url + '/refund-overpaid-cost-to-card'
            r = requests.post(url=url, json={
                'wash_id': self.wash_id,
                'wash_key': self.wash_key,
                'order_id': order.getId(),
                'overpaid': amount
            })
            if r.status_code == requests.codes.ok:
                log.info(u' '.join([u'Overpaid cost successfully refunded '
                                    u'to client, finance_id:', r.text]))
            elif r.status_code == 403:
                log.critical(u'You must set the valid auth credentials!')
            else:
                log.error(u' '.join([u'Failed to refund overpaid cost to client:', r.text]))
        except Exception as e:
            log.error(u' '.join([u'Failed to refund overpaid cost to client:', str(e)]))
