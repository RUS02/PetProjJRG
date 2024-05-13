CREATE USER DE_ML_user WITH PASSWORD 'de_ml_pass';
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO DE_ML_user ;

DROP SCHEMA if exists stage CASCADE;
DROP SCHEMA if exists dds CASCADE;
DROP SCHEMA if exists mart CASCADE;
CREATE SCHEMA if not exists stage;
CREATE SCHEMA if not exists mart;
CREATE SCHEMA if not exists dds;

create table if not exists
stage.rp5(
id serial primary key,
region varchar(100),
dt varchar(25),
t varchar(10)
);

create table if not exists
dds.regions(
id serial primary key,
region varchar(100) not null
);

create table if not exists
dds.temp(
id serial  primary key,
region_id int references dds.regions (id)  not null,
dt timestamptz(0) not null,
t numeric(4,1) not null
);

CREATE INDEX temp_dt_idx ON dds."temp" (dt);

create table if not exists
mart.regions(
id serial primary key,
region varchar(100) not null
);

create table if not exists
mart.avg_temp(
id serial  primary key,
region_id int references mart.regions (id) not null,
dt timestamptz(0) not null,
t numeric(4,1) not null
);

CREATE INDEX avg_temp_dt_idx ON mart."avg_temp" (dt);

drop view if exists mart.ml_data ;
CREATE OR REPLACE VIEW mart.ml_data
AS WITH dt_max AS (
         SELECT dt_m.dt_max,
            date_part('month'::text, dt_m.dt_max) AS mm,
            date_part('hour'::text, dt_m.dt_max - '09:00:00'::time without time zone::interval) AS hh,
            dt_m.region_id
           FROM ( SELECT max(dt) AS dt_max,
                    avg_temp.region_id
                   FROM mart.avg_temp
                  GROUP BY avg_temp.region_id) dt_m
        )
 SELECT reg.region,
    dt_max.dt_max,
        CASE
            WHEN dt_max.mm in (12,1,2) THEN 1
            ELSE 0
        END AS m0,
        CASE
            WHEN dt_max.mm in (3,4,5) THEN 1
            ELSE 0
        END AS m1,
        CASE
            WHEN dt_max.mm in (6,7,8) THEN 1
            ELSE 0
        END AS m2,
        CASE
            WHEN dt_max.mm in (9,10,11) THEN 1
            ELSE 0
        END AS m3,
    dt_max.hh,
    dt_9.t AS t_3,
    dt_6.t AS t_2,
    dt_3.t AS t_1,
    dt_now.t AS t0
   FROM dt_max
     JOIN ( SELECT avg_temp.dt,
            avg_temp.t,
            avg_temp.region_id
           FROM mart.avg_temp) dt_now ON dt_now.dt = dt_max.dt_max AND dt_now.region_id = dt_max.region_id
     JOIN ( SELECT avg_temp.dt,
            avg_temp.t,
            avg_temp.region_id
           FROM mart.avg_temp) dt_3 ON dt_3.dt = (dt_max.dt_max - '03:00:00'::time without time zone::interval) AND dt_3.region_id = dt_max.region_id
     JOIN ( SELECT avg_temp.dt,
            avg_temp.t,
            avg_temp.region_id
           FROM mart.avg_temp) dt_6 ON dt_6.dt = (dt_max.dt_max - '06:00:00'::time without time zone::interval) AND dt_6.region_id = dt_max.region_id
     JOIN ( SELECT avg_temp.dt,
            avg_temp.t,
            avg_temp.region_id
           FROM mart.avg_temp) dt_9 ON dt_9.dt = (dt_max.dt_max - '09:00:00'::time without time zone::interval) AND dt_9.region_id = dt_max.region_id
     JOIN ( SELECT regions.id,
            regions.region
           FROM mart.regions) reg ON reg.id = dt_max.region_id;
