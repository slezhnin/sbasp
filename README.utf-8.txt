Тестовое задание
================

Состоит из нескольких скриптов на Python (версии 2.6 и выше) и рассчитано на работу с СУБД MYSQL.

Тестовые файлы с данными генерируются скриптом "gen_test_data.py" во входной каталог.
Файлы из входного каталога загружаются скриптом "load_data.py" в базу данных.
Обработанные файлы перемещаются в выходной каталог.
Отчёты создаются скриптом "report_payment.py" в каталоге для отчётов.
Все конфигурационные параметры находятся в файле конфигурации "config.yml" (в формате YAML).
Все скрипты последовательно можно запустить shell-скриптом "runme.sh".

Зависимости прописаны в shell-скрипте dependency.sh и состоят из следующих библиотек:
- SQLAlchemy - библиотека для удобной работы с разными СУБД (так же содержит ORM, но это не используется в данном проекте);
- PyMYSQL - драйвер MYSQL;
- PyYAML - библиотека для загрузки YAML.

Использованные зависимости находятся в свободном доступе, поэтому к проекту не прилагаются.
Установку зависимостей лучше производить утилитой "pip" или "easy_install".

Описание файлов
---------------

config.py - загрузка конфигурации
config.yml - конфигурационный файл (формат YAML, имеются комментарии к параметрам)
db.py - описана структура данных для СУБД
dependency.sh - shell-скрипт для установки зависимостей
gen_test_data.py - скрипт для создания тестовых данных
load_data.py - скрипт для загрузки данных в СУБД
report_payment.py - скрипт для создания отчётов
report_template.yml - шаблон отчёта (формат YAML)
rollup.py - конструкция SQLAlchemy для добавления WITH ROLLUP к GROUP BY для MYSQL
runme.sh - пример запуска всех скриптов последовательно


(с) Сергей Лежнин, 2013
