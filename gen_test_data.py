#!/usr/bin/python
# coding=utf-8
from datetime import timedelta, datetime
import os
import random
from config import CONFIG


def payments_for_day():
    """
    Генерирует платежи для одного дня работы в соответствии с конфигом.
    Возвращает последовательность строк с платёжной информацией.
    """
    for osb, rp in CONFIG['osb_rp_list']:
        print ' Создание платежей для точки', str(osb) + '/' + str(rp)
        pay_n = 1  # Номер первого платежа
        for bic, account_template, max_n in CONFIG['bba']:
            max_number = max_n or 10
            print '  Банк:', bic, 'шаблон счета:', account_template, 'кол-во:', max_number
            random_numbers = range(1, max_number)
            random.shuffle(random_numbers)
            for account_n in random_numbers[:random.randint(1, max_number)]:
                account = account_template.format(account_n)
                print '   Счет:', account
                for n in range(1, random.randint(1, CONFIG['max_payment_per_point'] or 100)):
                    payment_sum = int(random.uniform(CONFIG['min_payment_sum'] or 1.0,
                                                     CONFIG['max_payment_sum'] or 1000.0) * 100)
                    commission = int(payment_sum * (CONFIG['commission'] or 0.01))
                    print '   ', n, 'платёж', payment_sum / 100, payment_sum % 100,
                    print 'комиссия', commission / 100, commission % 100
                    line = '{}||{}|{}||{}|{}|{}||{}|0|||{}||{}'.format(current_date, osb, rp, pay_n,
                                                                       payment_sum - commission,
                                                                       payment_sum, commission, bic,
                                                                       account)
                    pay_n += 1
                    print '   ', line
                    yield line + os.linesep


# Создание входного каталога при необходимости
if CONFIG.get('input_path', '') and not os.path.exists(CONFIG['input_path']):
    os.makedirs(CONFIG['input_path'])
# Начальная дата для генератора
period_start = datetime.strptime(CONFIG['period_start'], CONFIG['date_format']).date()
# Создание файлов с данными по дням
for d in (period_start + timedelta(n) for n in range(CONFIG['period_length'])):
    current_date = d.strftime(CONFIG['date_format'])
    current_filename = os.path.join(CONFIG.get('input_path', ''), current_date + '.txt')
    print 'Создаётся файл:', current_filename
    f = open(current_filename, 'w')
    f.writelines(payments_for_day())
    f.close()
