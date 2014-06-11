#!/usr/bin/python
# coding=utf-8
from datetime import timedelta, datetime
import os
from sqlalchemy.sql import select, func
from yaml import load
from rollup import rollup
from config import CONFIG
import db


def money_str(amount):
    """
    Преобразование денежной суммы в копейках в строку вида "руб.коп".
    """
    if not amount:
        return ''
    return '{:d}.{:02d}'.format(long(amount) / 100, long(amount) % 100)


def _gen_report_lines(connection, report_template, report_start, report_end, osbn, rpn):
    """
    Генерирует строки отчёта.
    Парвметры:
    connection - соединение с СУБД
    report_template - имя файла шаблона отчёта
    report_start - дата начала периода
    report_end - дата конца периода
    osbn - номер отделения
    rpn - номер точки приёма платежей
    Используется следующий SQL:
    SELECT pay_date, bic, account, pay_n, COUNT(pay_sum), SUM(pay_sum), SUM(pay_c)
    FROM sbasp WHERE pay_date BETWEEN :date1 AND :date2 AND osbn=:osbn AND rpn=:rpn
    GROUP BY pay_date, bic, account, pay_n WITH ROLLUP
    """
    fields = [db.table.c.pay_date, db.table.c.bic, db.table.c.account, db.table.c.pay_n,
              func.count(db.table.c.pay_sum), func.sum(db.table.c.pay_sum),
              func.sum(db.table.c.pay_c)]
    date_cond = db.table.c.pay_date.between(report_start, report_end)
    stmt = select(fields).where(date_cond).where(db.table.c.osbn == osbn).where(
        db.table.c.rpn == rpn).group_by(db.table.c.pay_date).group_by(db.table.c.bic).group_by(
        db.table.c.account).group_by(rollup(db.table.c.pay_n))
    result = connection.execute(stmt)
    report_file = open(report_template)
    template = load(report_file)
    report_file.close()
    date_format = CONFIG.get('date_display_format', CONFIG['date_format'])
    enc = CONFIG['report_encoding']
    report_data = {'osbn': osbn, 'rpn': rpn, 'report_start': report_start.strftime(date_format),
                   'report_end': report_end.strftime(date_format)}
    report_line = lambda name, data: template[name].rstrip().rstrip('|').format(**data).encode(enc)
    # Заголовок отчёта
    yield report_line('title', report_data)
    last_date, last_bic, last_account = None, None, None
    for pay_date, bic, account, pay_n, pay_count, pay_sum, pay_c in result:
        row_data = {'date': pay_date or last_date, 'bic': bic or last_bic,
                    'account': account or last_account, 'n': pay_n, 'count': pay_count,
                    'sum': money_str(pay_sum), 'commission': money_str(pay_c)}
        row_data['date'] = row_data['date'].strftime(date_format)
        row_data.update(report_data)
        if pay_date != last_date:
            if not pay_date:
                # Итог за период
                yield report_line('total', row_data)
                continue
            last_date = pay_date
            # Заголовок для даты
            yield report_line('subtitle1', row_data)
        if bic != last_bic:
            if not bic:
                # Подытог по дню
                yield report_line('subtotal1', row_data)
                continue
            last_bic = bic
            #  Заголовок для банка
            yield report_line('subtitle2', row_data)
        if account != last_account:
            if not account:
                # Подытог по банку
                yield report_line('subtotal2', row_data)
                continue
            last_account = account
            # Заголовок для счёта
            yield report_line('subtitle3', row_data)
        if not pay_n:
            # Подытог по счёту
            yield report_line('subtotal3', row_data)
        else:
            # Платёж
            yield report_line('detail', row_data)
    result.close()


def make_report(connection, report_filename, report_template, report_start, report_end, osbn, rpn):
    """
    Создание отчёта по точке приёма платежей за заданный период.
    Параметры:
    report_filename - имя файла отчёта
    report_template - имя файла шаблона отчёта
    report_start - дата начала периода
    report_end - дата конца периода
    osbn - номер отделения
    rpn - номер точки приёма платежей
    """
    print 'Создание файла отчёта:', report_filename
    report = open(report_filename, 'w')
    report.writelines(
        _gen_report_lines(connection, report_template, report_start, report_end, osbn, rpn))
    report.close()


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
    report_template = CONFIG['report_template_file']
    make_report(conn, report_filename, report_template, report_start, report_end, osbn, rpn)
conn.close()
