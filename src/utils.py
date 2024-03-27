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


def format_res_obj(obj):
    """Formats a response object"""

    obj['id'] = str(obj['_id'])

    if isinstance(obj.get('square_feet'), float):
        obj['square_feet'] = int(obj['square_feet'])

    return obj


def sort_by_date_key(obj):
    return datetime.fromisoformat(obj['updated_at'])


class DOS():
    """Helper functions."""

    def __init__(self):
        self.current_date = datetime.now().strftime('%c')

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

    def random_num(self, **kwargs):
        """Returns a random number as a string of a given length."""
        _len = int(kwargs.get('len', 0))

        if _len:
            rand_num = sample(range(1, _len+1), _len)
        else:
            rand_num = sample(range(1, 10), 5)

        rand_num = ''.join((str(x) for x in rand_num))

        return rand_num

    def make_reference(self, **kwargs):
        """Makes a reference."""

        item = f"""{kwargs.get('creator')}+{kwargs.get('game')}+{kwargs.get('amount')}+{self.current_date}+{kwargs.get('platform')}"""
        item = str(item).encode()
        data = b64encode(item)
        data = str(data).replace('b', '', 1).replace("'", '', 2)
        return data

    def current_time(self):
        """Returns the current time as a formatted string."""

        current_time = datetime.now()
        current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
        return current_time

    def check_time(self, given_time_str):
        """Check time."""

        given_time = datetime.strptime(given_time_str, '%Y-%m-%d %H:%M:%S')
        target_time = given_time + timedelta(minutes=30)
        current_time = datetime.now()
        time_difference = target_time - current_time
        minutes_remaining = max(int(time_difference.total_seconds() / 60), 0)
        return minutes_remaining
