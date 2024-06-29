FROM cr.yandex/crp1r8pht0n0gl25aug1/sprint-4:latest
WORKDIR /lessons/dags
#RUN rm -r sql
RUN rm -r sql/*.sql
RUN rm sprint3.py
#RUN mkdir sql
RUN mkdir ml
COPY dag.py .
COPY sql ./sql
COPY ml ./ml
COPY --chmod=644 ./airflow.cfg /opt/airflow/
COPY --chmod=644 ./airflow.cfg /.utils/
COPY --chmod=644 ./airflow-2-2-3.cfg /.utils/
RUN pip3 install scikit-learn==1.2.2
RUN /etc/init.d/postgresql start && psql postgresql://jovyan:jovyan@localhost:5432/de -f /lessons/dags/sql/init_db.sql && airflow connections add 'pg_connect' --conn-type 'postgres' --conn-login 'jovyan' --conn-password 'jovyan' --conn-host 'localhost' --conn-port '5432' --conn-schema 'de'
