FROM cr.yandex/crp1r8pht0n0gl25aug1/sprint-3:latest
WORKDIR /lessons/dags
RUN mkdir sql
RUN mkdir ml
COPY dag.py .
COPY sql ./sql
COPY ml ./ml
RUN pip3 install scikit-learn
RUN /etc/init.d/postgresql start && psql postgresql://jovyan:jovyan@localhost:5432/de -f /lessons/dags/sql/init_db.sql
#RUN airflow connections add 'pg_connect' --conn-type 'postgres' --conn-login 'jovyan' --conn-password 'jovyan' --conn-host 'localhost' --conn-port '5432' --conn-schema 'de'