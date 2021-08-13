# -*- coding: utf-8 -*-
import mimetypes
import os
import smtplib
import logging
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class EmailNotifier(object):
    def __init__(self, sender, receivers, smtpServer, login, password):
        self._sender = sender
        self._receivers = receivers
        self._smtpServer = smtpServer
        self._login = login
        self._password = password
        self._log = logging.getLogger(__name__)

    def notify(self, message):
        msg = MIMEMultipart('alternative')
        msg['subject'] = "Automatic notification"
        msg['to'] = ", ".join(self._receivers)
        msg['from'] = self._sender
        # msg.preamble = """Это сообщение сгенерировано автоматически."""
        body = MIMEText(message, 'plain')
        msg.attach(body)
        try:
            smtpObj = smtplib.SMTP(self._smtpServer)
            smtpObj.starttls()
            smtpObj.login(self._sender, self._password)
            smtpObj.sendmail(self._sender, self._receivers, msg.as_string())
            self._log.info("Email sended successfully")
        except smtplib.SMTPException as e:
            self._log.error("Unable to send email: {}".format(e))

    def notifyFile(self, filePath, message="", filename=None):
        # type: (str, str, str) -> None
        """для отправки файла с сообщением или без
        :param filename: str имя файла при отправке
        :type message: str текст сообщения
        :type filePath: str путь к файлу
        """
        msg = MIMEMultipart('alternative')
        msg['subject'] = "Automatic notification"
        msg['to'] = ", ".join(self._receivers)
        msg['from'] = self._sender
        body = MIMEText(message, 'plain')
        msg.attach(body)
        try:
            attachment = open(filePath, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            if not filename:
                filename = os.path.basename(filePath)
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(p)
        except Exception as e:
            self._log.error("Email error. This is path to file is not resolve: {}".format(e))
        try:
            smtpObj = smtplib.SMTP(self._smtpServer)
            smtpObj.starttls()
            smtpObj.login(self._sender, self._password)
            smtpObj.sendmail(self._sender, self._receivers, msg.as_string())
            self._log.info("Email sended successfully")
        except smtplib.SMTPException as e:
            self._log.error("Unable to send email: {}".format(e))

    def notifyFiles(self, filePaths=None, message="", messageTheme="Automatic notification"):
        # type: (list, str) -> None
        """для отправки файлов в неогр. кол-ве
        :type message: str текст сообщения
        :type filePaths: list пути к файлам
        """
        msg = MIMEMultipart()
        msg['subject'] = messageTheme
        msg['to'] = ", ".join(self._receivers)
        msg['from'] = self._sender
        body = MIMEText(message, 'plain', 'utf-8')
        msg.attach(body)
        if filePaths is not None:
            for each_file_path in filePaths:
                ctype, encoding = mimetypes.guess_type(each_file_path)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                file_name = os.path.basename(each_file_path)
                fp = open(each_file_path, "rb")
                part = MIMEBase(maintype, subtype)
                part.add_header('Content-Transfer-Encoding', 'base64')
                part.set_payload((fp).read())
                fp.close()
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=file_name)
                msg.attach(part)

        try:
            smtpObj = smtplib.SMTP(self._smtpServer)
            smtpObj.starttls()
            smtpObj.login(self._sender, self._password)
            smtpObj.sendmail(self._sender, self._receivers, msg.as_string())
            smtpObj.quit()
            self._log.info("Email sended successfully")
        except smtplib.SMTPException as e:
            self._log.error("Unable to send email: {}".format(e))
