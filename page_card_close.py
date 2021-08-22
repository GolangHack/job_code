# -*- coding: utf-8 -*-
import threading
import time

from data_storage.database import Card
from data_storage.database.settingsManager import SettingsManager
from htmlpy_core.html_page import HtmlPage
#from threading import Timer
from pyutils.delay import Delay
from operation_scenario import OperationScenario
import logging
import config
from pyutils.checkInternet import checkInternet

log = logging.getLogger(__name__)


class PageCardClose(HtmlPage):

    def onButtonClick(self, button, arg):
        if button == "main":
            self.operationScenario.disableReceiveCards()
            self.switchTo("PageMain")
        if button == "phone":
            self.switchTo("PageInputPhone")

    def onEnter(self, prevPage, *args, **kwargs):
        log.info("Enter page")
        self.operationScenario = self.getVariable('operationScenario')
        self.operationScenario.canGoToSleepMode = False

        # Если была приостановлена работа card_close - продолжить

        if self.operationScenario.cardCloseRefuse:
            threading.Thread(target=self.cardEvent).start()
            print(u"Восстанавливаю работу с функции self.cardEvent")
            log.info(u"Flag cardCloseRefuse is enabled. Start cardEvent.")
            return None

        if not checkInternet():
            self.setElementEnabled("phone", False)

        self.operationScenario.enableCardReader()
        self.emulate = self.getVariable('emulate')
        self.emulate_client_card = self.getVariable('emulate_client_card')

        if config.getProperty('debug_emualete_bank_card', default=False, _type='bool') and\
                (self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_BANK_CARD):
            Delay.once(self, 1, pageBankExchange)

        elif config.getProperty("emulate_client_card", False, _type='bool') and self.operationScenario.receiveCardsEnabled:
            print("Enable the emulate client card. Insert test card.")
            # эмуляция клиентской карты
            self.operationScenario.setCardType(OperationScenario.CARD_TYPE_MIFARE)
            self.operationScenario.setCardUid(config.getProperty("debug_card_uid", "1185694077182080"))
            card = Card.Card(self.operationScenario.getCardUid())
            self.operationScenario.setClientCard(card)
            self.operationScenario.setCardSubType(card.type)
            self.operationScenario.setCardBalance(card.balance)
            # self.operationScenario.setCardSubType(config.getProperty("debug_card_sub_type", "companycard"))
            #Timer(1, self.cardEvent).start()
            Delay.once(self, 1, CardEvent)


        # при бездействии 60 сек, выкинуть на главный экран
        def inactivityAction():
            log.info("Card inactivity action executed!")
            self.operationScenario.disableReceiveCards()
            self.switchTo("PageMain")
        self.inactivityTimer = Delay.once(self, 60, inactivityAction)

        #self.inactivityTimer.start()

    def onExit(self, nextPage, *args, **kwargs):
        log.info("Exit page")
        #self.inactivityTimer.cancel()
        self.setVariable(amount_desc=u'')

    def cardEvent(self):
        log.info("cardEvent()")
        self.getRequestPhoneForClientCardEnabled = self.operationScenario.getRequestPhoneForClientCardEnabled()
        currentClientCard = self.operationScenario.getClientCard()
        'Проверка карты на возможность показывать сообщения о привязке телефона к карте'
        if self.operationScenario.getCardType() == OperationScenario.CARD_TYPE_MIFARE:
            requestEnterPhoneEnabled = currentClientCard.getProperty("request_enter_phone_enabled", "bool")
            if (not currentClientCard.isPhoneBinded() and
                    requestEnterPhoneEnabled and
                    not self.operationScenario.cardCloseRefuse):
                self.switchTo("PageAddPhoneInCard")
                return None
        if self.operationScenario.cardCloseRefuse:
            print("Refuse cardEvent")
            self.operationScenario.disablePageCardCloseRefuse()

        if self.operationScenario.getCardClosePurpose() == OperationScenario.CARD_CLOSE_PURPOSE_FILL_CARD:
            if (self.operationScenario.getCardType() == OperationScenario.CARD_TYPE_MIFARE):
                if self.operationScenario.atolModeOnlyQrCodeCheck():
                    self.switchTo("PageSelPay", pay_description=self.operationScenario.generateDescription())
                else:
                    if self.operationScenario.getHasPaper():
                        self.switchTo("PageSelPay", pay_description=self.operationScenario.generateDescription())
                    else:
                        self.switchTo("PageWarning", next="PageSelPay",
                                      warning_text=u'В данный момент терминал не выдаёт бумажные чеки.<br>'
                                                   u'Хотите продолжить?')
            elif (self.operationScenario.getCardType() == OperationScenario.CARD_TYPE_MIFARE_NEW):
                self.switchTo("PageError", page_title=u'Внимание',
                              error_text=u'Новая клиентская карта была создана.<br>'
                                         u'Повторите операцию')
            else:
                self.switchTo("PageError", error_text=u'Невозможно пополнить банковскую карту с терминала')
        elif self.operationScenario.getCardClosePurpose() == OperationScenario.CARD_CLOSE_PURPOSE_SHOW_BALANCE:
            if (self.operationScenario.getCardType() == OperationScenario.CARD_TYPE_MIFARE):
                # Карта админа
                if (currentClientCard.type == "ADMINISTRATOR" or
                        config.getProperty('debug_all_card_administr', False, 'bool')):
                    self.switchTo("PageAdministartorMenu")

                # Карта оператора
                elif (currentClientCard.type == 'OPERATOR' or
                      config.getProperty('operator_card_emulate', False, 'bool')):
                    self.switchTo('PageOperatorMenu')

                # Обычная карта
                else:
                    if self.operationScenario.atolModeOnlyQrCodeCheck():
                        self.switchTo("PageCardBalance")
                    else:
                        if self.operationScenario.getHasPaper():
                            self.switchTo("PageSelBalance")
                        else:
                            self.switchTo("PageCardBalance")
            elif (self.operationScenario.getCardType() == OperationScenario.CARD_TYPE_MIFARE_NEW):
                self.switchTo("PageError", page_title=u'Внимание',
                              error_text=u'Новая клиентская карта была создана.<br>'
                                         u'Повторите операцию пополнения карты')

        # Оплата мойки робото клиентской картой
        elif self.operationScenario.getCardClosePurpose() == OperationScenario.CARD_CLOSE_PURPOSE_PAY:
            if self.operationScenario.getPaySource() == OperationScenario.PAY_SOURCE_CLIENT_CARD:
                if (self.operationScenario.getCardType() == OperationScenario.CARD_TYPE_MIFARE):
                    spending_sum = self.operationScenario.getSpendingSum()
                    if (self.operationScenario.getCardBalance() >= spending_sum or
                            currentClientCard.account_type == "CREDIT"):
                        # отключаем кнопки перед печатью чека
                        self.setElementEnabled("main", False)
                        self.setElementEnabled("phone", False)
                        self.operationScenario.setMoneyInserted(spending_sum)
                        self.operationScenario.pay()
                        if self.operationScenario.getPayDestination() == OperationScenario.PAY_DEST_ROBOT:
                            self.switchTo("PageQueueNumber")
                        else:
                            self.switchTo("PageMain")
                    else:
                        log.info("Not enough money: %srub. On card: %s. Needed: %s", \
                                        self.operationScenario.getCardBalance(), \
                                        self.operationScenario.getCardUid(), \
                                        self.operationScenario.getSpendingSum()\
                                        )
                        self.switchTo("PageError", error_text=u'На счете недостаточно средств: ' +
                                                              str(self.operationScenario.getCardBalance()) + u' p.')

        elif self.operationScenario.getCardClosePurpose() == OperationScenario.CARD_CLOSE_PURPOSE_BUY_CARD:
            if self.operationScenario.getCardBalance() >= self.operationScenario.getSpendingSum():
                self.operationScenario.pay()
                self.switchTo("PageMain")
            else:
                log.info("Not enough money: %srub. On card: %s. Needed: %s", \
                                self.operationScenario.getCardBalance(), \
                                self.operationScenario.getCardUid(), \
                                self.operationScenario.getSpendingSum()\
                                )
                self.switchTo("PageError", error_text=u'На карте недостаточно средств: ' +
                                                      str(self.operationScenario.getCardBalance()) + u' p.')

        elif self.operationScenario.getCardClosePurpose() == OperationScenario.CARD_CLOSE_PURPOSE_COMPANY_CHANGE_CARD:
            self.switchTo("PageChangeCard")
