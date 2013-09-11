# coding=utf-8
from sqlalchemy import create_engine, String, UniqueConstraint
from sqlalchemy import Table, Column, Integer, MetaData, Date

from config import CONFIG


engine = create_engine(CONFIG['database_connection_string'], echo=True)

metadata = MetaData()

table = Table(CONFIG['database_table_name'], metadata, Column('id', Integer, primary_key=True),
              Column('pay_date', Date), Column('osbn', Integer), Column('rpn', Integer),
              Column('pay_n', Integer), Column('pay_sum', Integer), Column('pay_c', Integer),
              Column('bic', String(10)), Column('account', String(20)),
              UniqueConstraint('pay_date', 'osbn', 'rpn', 'pay_n', name='pay_unique'))

metadata.create_all(engine)