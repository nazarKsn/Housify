#!/usr/bin/env python3
"""Class with helper functions"""
import requests
import smtplib
from datetime import datetime, timedelta
from device_detector import DeviceDetector
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import sample
from base64 import b64encode
import bcrypt


class Utils():
    """Helper functions."""

    @staticmethod
    def is_bot(self, ua):
        """Checks if a device is a bot.
        
        Args:
            ua (str): The user agent string.
        """
    
        device = DeviceDetector(ua).parse()
        if device.is_bot() or device.os_name() == '':
            return True
        else:
            return False
    
    @staticmethod
    def format_res_obj(obj):
        """Formats a response object"""
        
        obj['id'] = str(obj['_id'])

        if isinstance(obj.get('square_feet'), float):
            obj['square_feet'] = int(obj['square_feet'])

        return obj
    
    @staticmethod
    def sort_by_date_key(obj):
        """Returns a key for sorting an object by update_at"""
        return datetime.fromisoformat(obj['updated_at'])
    
    @staticmethod
    def encrypt_password(password):
        """Encrypts a password and returns it"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    def check_password(password, encrypted):
        """Checks if a password matches an encrypted password"""
        return bcrypt.checkpw(password.encode(), encrypted)
    
    @staticmethod
    def send_telegram_message(self, bot, chat_id, message):
        """Sends a Telegram message."""

        api_url = f'https://api.telegram.org/bot{bot}/sendMessage'
        params = {'chat_id': chat_id, 'text': message}

        try:
            response = requests.post(api_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error sending message: {e}")
            return None
    
    @staticmethod
    def send_email_notification(self, host, port, sndr_email, sndr_pwd,
                                rec_mail, subj, msg):
        """Sends an email."""

        message = MIMEMultipart()
        message['From'] = sndr_em
        message['To'] = rec_mail
        message['Subject'] = subj
        message.attach(MIMEText(msg, 'plain'))

        try:
            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
            smtp_server.starttls()
            smtp_server.login(sndr_email, sndr_pwd)
        except smtplib.SMTPException as e:
            print(f"Error connecting to the SMTP server: {e}")
            return False

        try:
            smtp_server.sendmail(sndr_email, rec_mail, message.as_string())
            smtp_server.quit()
            print("Email sent successfully.")
            return True
        except smtplib.SMTPException as e:
            print(f"Error sending the email: {e}")
            return False