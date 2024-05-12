truncate table mart.avg_temp;
delete from mart.regions;
insert into mart.regions select * from dds.regions;

insert into mart.avg_temp(region_id,t,dt)
select region_id,avg(t)::numeric(4,1) t,dt::timestamp(0) from 
(select region_id,t, date_trunc('hour', dt) as dt from dds.temp) as trun
group by region_id,dt;
