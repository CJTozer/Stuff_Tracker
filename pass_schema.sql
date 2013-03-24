drop table if exists authentication;
create table authentication (
  user_id integer primary key autoincrement,
  username string not null,
  password string not null
);