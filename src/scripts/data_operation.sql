update bim_spec set attrs_see = b.attrs_m from bim_spec b where 
  bim_spec.desc like 'See %' and 
	b.desc not like 'See %' and 
	b.code like substr(bim_spec.desc, 5,  length(bim_spec.desc)-3)||" %" AND
	bim_spec.level = b.level;

select bim_spec.gid a_gid, bim_spec.desc a_desc, bim_spec.level a_level,bim_spec.attrs_see a_attrs_see, b.gid, b.code,b.level, b.attrs_m from bim_spec, bim_spec b where
    bim_spec.desc like 'See %' and 
	b.desc not like 'See %' and 
	b.code like substr(bim_spec.desc, 5,  length(bim_spec.desc)-3)||" %" AND
	bim_spec.level = b.level;

alter table bim_spec add column attrs_total varchar;

update bim_spec set attrs_total = attrs||"," || attrs_see;

-- concatenate string to ignore NULL
update bim_spec set attrs_total = coalesce(attrs_m, attrs_see);



drop table if exists bim_spec_fundamental;
create table bim_spec_fundamental as select gid, level, code, desc, attrs, attrs_m from bim_spec limit 0;

insert into bim_spec_fundamental(level, desc, code) values(100, 'The Model Element may be graphically represented in the Model with a symbol or other generic representation, but does not 
satisfy the requirements for LOD 200. Information related to the Model Element (e.g., cost per square foot, tonnage of HVAC, etc.) can 
be derived from other Model Elements.', 'Fundamental LOD Definitions');

insert into bim_spec_fundamental(level, desc, code) values(200, 'The Model Element is generically and graphically represented within the Model with approximate quantity, size, shape, 
location, and orientation.', 'Fundamental LOD Definitions');

insert into bim_spec_fundamental(level, desc, code) values(300, 'The Model Element, as designed, is graphically represented within the Model such that its quantity, size, shape, location, and 
orientation can be measured.', 'Fundamental LOD Definitions');

insert into bim_spec_fundamental(level, desc, code) values(350, 'The Model Element, as designed, is graphically represented within the Model such that its quantity, size, shape, location, 
orientation, and interfaces with adjacent or dependent Model Elements can be measured.', 'Fundamental LOD Definitions');

insert into bim_spec_fundamental(level, desc, code) values(400, 'The Model Element is graphically represented within the Model with detail sufficient for fabrication, assembly, and 
installation.', 'Fundamental LOD Definitions');

insert into bim_spec_fundamental(level, desc, code) values(500, 'The Model Element is a graphic representation of an existing or as-constructed condition developed through a combination of 
observation, field verification, or interpolation. The level of accuracy shall be noted or attached to the Model Element.', 'Fundamental LOD Definitions');

select * from bim_spec_fundamental;



--select gid, includes, desc, level, code, attrs_total from bim_spec_final;
select a.gid, includes, desc, level, code, attrs_total, 
case when b.gid is not null then 1 else 0 end as shape,
case when c.gid is not null then 1 else 0 end as size,
case when d.gid is not null then 1 else 0 end as type,
case when e.gid is not null then 1 else 0 end as concrete,
case when f.gid is not null then 1 else 0 end as concretefloor
from bim_spec_final as a
left outer join 
(
select gid from bim_spec_final where desc like '%shape%'
) as b on a.gid = b.gid 
left outer join 
(
select gid from bim_spec_final where desc like '%size%'
) as c on a.gid = c.gid 
left outer join 
(
select gid from bim_spec_final where desc like '%type%'
) as d on a.gid = d.gid 
left outer join 
(
select gid from bim_spec_final where desc like '%Concrete,%'
) as e on a.gid = e.gid 
left outer join 
(
select gid from bim_spec_final where desc like '%Concrete Floor,%'
) as f on a.gid = f.gid;
