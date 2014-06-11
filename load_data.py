#!/usr/bin/python
# coding=utf-8
import os
from datetime import datetime
import shutil
from config import CONFIG
import db


def parse_line(line):
    """
    Разбор строки из файла.
    Возвращает разобранную строку в виде карты
    {pay_date: ДАТА, osbn: NОСБ, rpn: NТП, pay_n: NПЛАТЕЖА, pay_sum: СУММА, pay_c: КОМИССИЯ,
        bic: БИК, account: СЧЁТ}
    или None, если разбор не удался
    """
    if '|' in line:
        raw_data = line.split('|')
        if len(raw_data) == 16:
            return {
                'pay_date': datetime.strptime(raw_data[0].strip(), CONFIG['date_format']).date(),
                'osbn': int(raw_data[2].strip()), 'rpn': int(raw_data[3].strip()),
                'pay_n': int(raw_data[5].strip()), 'pay_sum': int(raw_data[7].strip()),
                'pay_c': int(raw_data[9].strip()), 'bic': raw_data[13].strip(),
                'account': raw_data[15].strip()}
    return None


def load_file(filename):
    """
    Загрузка данных из файла.
    Работает как генератор, т.е. возвращает последовательность карт
    из разобранных функцией parse_line() строк
    [{}, ...]
    """
    print 'Загрузка файла:', filename
    infile = open(filename)
    for line in infile.readlines():
        line = line.rstrip('\r\n')
        print line,
        data = parse_line(line)
        if data:
            print ' ' * (75 - len(line)), '[З]'
            yield data
        else:
            print ' ' * (75 - len(line)), '[П]'
    infile.close()


def load_files(connection):
    """
    Загрузка данных из файлов входного каталога.
    После загрузки данных файл перемещается в выходной каталог.
    """
    # Создание выходного каталога при необходимости
    if CONFIG.get('output_path', '') and not os.path.exists(CONFIG['output_path']):
        os.makedirs(CONFIG['output_path'])
    input_path = CONFIG.get('input_path', '')
    # Сканируем входные файлы
    for f in os.listdir(input_path):
        fn = os.path.join(input_path, f)
        if os.path.isfile(fn):
            # Вставляем в таблицу данные из файла
            result = connection.execute(db.table.insert(), [d for d in load_file(fn)])
            result.close()
            if CONFIG.get('output_path', ''):
                # Перемещение файла из входного в выходной каталог
                shutil.move(fn, os.path.join(CONFIG['output_path'], f))


print 'Загрузка платёжных данных...'
conn = db.engine.connect()
load_files(conn)
conn.close()

