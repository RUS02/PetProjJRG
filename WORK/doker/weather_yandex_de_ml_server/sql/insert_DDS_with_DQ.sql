insert into dds.regions (region)
select distinct region from stage.rp5 where region not in (select region from dds.regions );

insert into dds.temp (region_id,dt,t)
select r.id, (rp.dt)::timestamptz(0),(rp.t)::numeric(4,1)
from stage.rp5 as rp
left join dds.regions as r 
on r.region=rp.region
where (t ~ '^["+","-"]{0,1}[0-9]*.?[0-9]*$')
and (r.id,(rp.dt)::timestamptz(0)) not in (select region_id, dt from dds.temp);

delete from dds.temp where dt<dt - interval '7 day';
