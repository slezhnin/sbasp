# coding=utf-8
from sqlalchemy import create_engine, String
from sqlalchemy import Table, Column, Integer, MetaData, Date

from config import config


engine = create_engine(config()['database_connection_string'], echo=True)

metadata = MetaData()

table = Table('sbassp', metadata, Column('id', Integer, primary_key=True), Column('pay_date', Date),
              Column('osbn', Integer), Column('rpn', Integer), Column('pay_n', Integer),
              Column('pay_sum', Integer), Column('pay_c', Integer), Column('bic', String),
              Column('account', String))