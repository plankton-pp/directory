import pandas as pd
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import re

username='root'     
password='dtac1800' 
host="localhost"
port_db="3306"

Base=declarative_base()
engine=create_engine(f'mysql+mysqldb://{username}:{password}@{host}:{port_db}/cactidb')

class Ex_fiberloss_id(Base):
    __tablename__='ex_fiberloss_id'
    fiber_id=Column(Integer,primary_key=True)
    domain=Column(VARCHAR(20))
    physicalconns=Column(Integer)
    conn_name=Column(VARCHAR(30))
    a_design=Column(Float)
    z_design=Column(Float)
    a_from_label=Column(VARCHAR(30))
    a_to_label=Column(VARCHAR(30))
    z_from_label=Column(VARCHAR(30))
    z_to_label=Column(VARCHAR(30))
    fiber_length=Column(Float)

class Ex_fiberloss_record(Base):
    __tablename__='ex_fiberloss_record'
    record_id=Column(Integer,primary_key=True)
    domain=Column(VARCHAR(20))
    physicalconns=Column(Integer)
    date=Column(DateTime, default=datetime.datetime.utcnow)
    a_calc_spanloss=Column(Float)
    a_calc_spanloss=Column(Float)


Base=declarative_base()

table_objects = [Ex_fiberloss_id.__table__,Ex_fiberloss_record.__table__]
Base.metadata.create_all(engine,tables=table_objects)

# if __name__ == "__main__":
#     Ex_fiberloss_id.__table__.drop(engine)
#     Ex_fiberloss_record.__table__.drop(engine)
