# coding=utf-8
import time
from datetime import datetime
from time import sleep


def current_datetime():
    return datetime.now()


def culc_after_year(year):
    """
    :param year: 年数（int）
    :return: 今から年数後の日付
    """
    return datetime.fromtimestamp(
        time.mktime((datetime.now().year + year, datetime.now().month, datetime.now().day, 0, 0, 0, 0, 0, 0)))


def culc_before_year(year):
    """
    :param year: 年数（int）
    :return: 今から年数前の日付
    """
    return datetime.fromtimestamp(
        time.mktime((datetime.now().year - year, datetime.now().month, datetime.now().day, 0, 0, 0, 0, 0, 0)))


def culc_after_month(month):
    """
    :param month: 月数（int）
    :return: 今から月数後の日付
    TODO:月ごとの日数の考慮できてない!!
    """
    return datetime.fromtimestamp(
        time.mktime((datetime.now().year, datetime.now().month + month, datetime.now().day, 0, 0, 0, 0, 0, 0)))


def culc_before_month(month):
    """
    :param month: 月数（int）
    :return: 今から月数前の日付
    TODO:月ごとの日数の考慮できてない!!
    """
    return datetime.fromtimestamp(
        time.mktime((datetime.now().year, datetime.now().month - month, datetime.now().day, 0, 0, 0, 0, 0, 0)))


def sleep_second(second):
    print('{}秒処理停止...'.format(second))
    sleep(second)
