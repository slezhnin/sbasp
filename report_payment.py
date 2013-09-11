#!/usr/bin/python
# coding=utf-8
from datetime import timedelta, datetime
import os
from sqlalchemy.sql import select, func
from rollup import rollup
from config import CONFIG
import db


def money_str(amount):
    """
    Преобразование денежной суммы в копейках в строку вида "руб.коп".
    """
    if not amount:
        return ''
    return str(long(amount) / 100) + '.' + str(long(amount) % 100)


def make_report(connection, report_filename, report_start, report_end, osbn, rpn):
    """
    Создание отчёта по точке приёма платежей за заданный период.
    Параметры:
    report_filename - имя файла отчёта
    report_start - дата начала периода
    report_end - дата конца периода
    osbn - номер отделения
    rpn - номер точки приёма платежей
    """
    print 'Создание файла отчёта:', report_filename
    stmt = select([db.table.c.pay_date, db.table.c.bic, db.table.c.account, db.table.c.pay_n,
        db.table.c.pay_sum, func.sum(db.table.c.pay_sum), func.count(db.table.c.pay_sum),
        db.table.c.pay_c, func.sum(db.table.c.pay_c)]).where(
        db.table.c.pay_date.between(report_start, report_end)).where(db.table.c.osbn == osbn).where(
        db.table.c.rpn == rpn).group_by(db.table.c.pay_date).group_by(db.table.c.bic).group_by(
        db.table.c.account).group_by(rollup(db.table.c.pay_n))
    result = connection.execute(stmt)
    report = open(report_filename, 'w')
    report.write(
        'Отчет о точке приема {}/{} точки приема за период с {} по {}\n\n'.format(osbn, rpn,
            report_start, report_end))
    last_date, last_bic, last_account = None, None, None
    for pay_date, bic, account, pay_n, pay_sum, pay_sum_total, pay_count, pay_c, pay_c_total in result:
        if pay_date != last_date:
            last_date = pay_date
            report.write('Дата {}\n\n'.format(pay_date))
        if bic != last_bic:
            last_bic = bic
            report.write('Банк {}\n\n'.format(bic))
        if account != last_account:
            last_account = account
            report.write('Счёт {}\n\n#    Сумма      Комиссия\n\n'.format(account))
        if not pay_n:
            # Субтотал по счёту
            report.write('Итого по счёту {}\n{} {} {}\n\n'.format(account, pay_count,
                money_str(pay_sum_total), money_str(pay_c_total)))
        else:
            report.write('{} {} {}\n'.format(pay_n, money_str(pay_sum), money_str(pay_c)))
    result.close()


# Выходной каталог для отчётов
report_path = CONFIG.get('report_path', '')
# Создание входного каталога при необходимости
if report_path and not os.path.exists(report_path):
    os.makedirs(report_path)
# Начальная дата для отчёта
report_start = datetime.strptime(CONFIG['report_start'], CONFIG['date_format']).date()
# Конечная дата для отчёта
report_end = report_start + timedelta(CONFIG['report_length'] - 1)
print 'Формирование отчёта с {} по {}'.format(report_start, report_end)
conn = db.engine.connect()
report_name_template = report_start.strftime(CONFIG['report_name_format'])
# Цикл по отделениям и точкам приёма платежей
for osbn, rpn in CONFIG['osb_rp_list']:
    report_name = report_name_template.format(CONFIG['report_length'], osbn, rpn) + CONFIG[
        'report_file_format']
    report_filename = os.path.join(report_path, report_name)
    make_report(conn, report_filename, report_start, report_end, osbn, rpn)
conn.close()
