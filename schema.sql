drop table if exists resources;
create table resources (
  res_id integer primary key autoincrement,
  name string not null
);

drop table if exists components;
create table components (
  comp_id integer primary key autoincrement,
  res_id integer,
  name string not null,
  time integer,
  complete boolean
);

drop table if exists resource_time_tracking;
create table resource_time_tracking (
  timestamp float,
  res_id integer,
  time_spent integer
);