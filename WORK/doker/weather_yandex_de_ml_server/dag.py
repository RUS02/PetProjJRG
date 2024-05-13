import time
import requests
import json
import pandas as pd
import requests

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.http_hook import HttpHook

postgres_conn_id = 'pg_connect'


from bs4 import BeautifulSoup
import numpy as np
#ML
import sklearn
import pickle
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler, StandardScaler  #для масштабирования данных
from sklearn.linear_model import LinearRegression #лдинейная регрессия

X_col=['m0', 'm1', 'm2', 'm3', 'hh', 'T-3', 'T-2', 'T-1', 'T0']

lr1 = pickle.load(open('/lessons/dags/ml/lr1.sav', 'rb')) 
lr2 = pickle.load(open('/lessons/dags/ml/lr2.sav', 'rb')) 
lr3 = pickle.load(open('/lessons/dags/ml/lr3.sav', 'rb')) 
lr4 = pickle.load(open('/lessons/dags/ml/lr4.sav', 'rb')) 
X_scale = pickle.load(open('/lessons/dags/ml/X_scale.sav', 'rb')) 
y_scale = pickle.load(open('/lessons/dags/ml/y_scale.sav', 'rb')) 

def get_weather_rp5(pg_schema, pg_table):
    soup = BeautifulSoup(requests.get("https://rp5.ru/rss/5483/ru").text, 'html.parser')
    title=soup.find_all('title')[0].text
    updated=soup.find_all('updated')[0].text
    cnt=0
    for tag in soup.find_all('span', {'class': 't_0'}):
        t=tag.text
        print(t)
        if cnt==0:
            df = pd.DataFrame({'region': [title],'dt': [updated],'t': [tag.text]})
        else:
            df.loc[cnt] = [title, updated, tag.text]
        cnt+=1
    postgres_hook = PostgresHook(postgres_conn_id)
    engine = postgres_hook.get_sqlalchemy_engine()
    row_count = df.to_sql(pg_table, engine, schema=pg_schema, if_exists='append', index=False)
    print(f'{row_count} rows was inserted')

def ml_weather(pg_schema, pg_table):
    postgres_hook = PostgresHook(postgres_conn_id)
    engine = postgres_hook.get_sqlalchemy_engine()
    #Считываем историю
    df = pd.read_sql_query('select  region,dt_max,m0,m1,m2,m3,hh,T_3 as "T-3",T_2 as "T-2", T_1 as "T-1", T0 as "T0" from mart.ml_data limit 100;', engine) 
    df2=df.drop(['region','dt_max'],axis=1)
     
    his = open('/var/tmp/data_history_x.txt', 'w')
    fut = open('/var/tmp/data_future_x.txt', 'w')
    if len(df.index)==0:
        his.write('Прогноз невозможен\n')
        his.write('Нужно накопить данные\n')
        his.write('за 10 часов\n')
    else:
        #Строим прогноз
        t1=y_scale.inverse_transform(lr1.predict(PolynomialFeatures(3).fit_transform(X_scale.transform(df2))))[0]
        t2=y_scale.inverse_transform(lr2.predict(PolynomialFeatures(3).fit_transform(X_scale.transform(df2))))[0]
        t3=y_scale.inverse_transform(lr3.predict(PolynomialFeatures(3).fit_transform(X_scale.transform(df2))))[0]
        t4=y_scale.inverse_transform(lr4.predict(PolynomialFeatures(3).fit_transform(X_scale.transform(df2))))[0]

        for i in range(len(df.index)):
            his.write(df.region[i]+'\n')
            his.write(str(df.dt_max[i].to_pydatetime())[:16]+' '+str(df["T0"][i])[:4]+'\n')
            his.write(str(df.dt_max[i].to_pydatetime()-timedelta(hours=3))[:16]+' '+str(df["T-1"][i])[:4]+'\n')
            his.write(str(df.dt_max[i].to_pydatetime()-timedelta(hours=6))[:16]+' '+str(df["T-2"][i])[:4]+'\n')
            his.write(str(df.dt_max[i].to_pydatetime()-timedelta(hours=9))[:16]+' '+str(df["T-3"][i])[:4]+'\n')
            
            fut.write(df.region[i]+'\n')
            fut.write(str(df.dt_max[i].to_pydatetime()+timedelta(hours=3))[:16]+' '+str(t1[i])[:4]+'\n')
            fut.write(str(df.dt_max[i].to_pydatetime()+timedelta(hours=6))[:16]+' '+str(t2[i])[:4]+'\n')
            fut.write(str(df.dt_max[i].to_pydatetime()+timedelta(hours=9))[:16]+' '+str(t3[i])[:4]+'\n')
            fut.write(str(df.dt_max[i].to_pydatetime()+timedelta(hours=12))[:16]+' '+str(t4[i])[:4]+'\n')
        
    his.close()
    fut.close()


args = {
    "owner": "JRG",
    'email': ['student@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

with DAG(
        'weather_predict',
        default_args=args,
        description='dag for diplom',
        catchup=False,
        schedule_interval='*/15 * * * *', 
        start_date= datetime(2022, 1, 1),
        #end_date=datetime.today() - timedelta(days=1),
) as dag:

    init_stg = PostgresOperator(
        task_id='init_stg',
        postgres_conn_id=postgres_conn_id,
        sql="sql/init_stg.sql")

    get_weather_rp5 = PythonOperator(
        task_id='get_weather_rp5',
        python_callable=get_weather_rp5,
        op_kwargs={'pg_schema': 'stage',
                   'pg_table' : 'rp5'})

    insert_DDS_with_DQ = PostgresOperator(
        task_id='insert_DDS_with_DQ',
        postgres_conn_id=postgres_conn_id,
        sql="sql/insert_DDS_with_DQ.sql")

    insert_MART_with_AVG = PostgresOperator(
        task_id='insert_MART_with_AVG',
        postgres_conn_id=postgres_conn_id,
        sql="sql/insert_MART_with_AVG.sql")

    ml_weather = PythonOperator(
        task_id='ml_weather',
        python_callable=ml_weather,
        op_kwargs={'pg_schema': 'mart',
                   'pg_table' : 'ml_data'})

init_stg >> get_weather_rp5 >> insert_DDS_with_DQ >> insert_MART_with_AVG >>  ml_weather
