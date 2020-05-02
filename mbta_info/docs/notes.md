Find hanging queries:

`SELECT pid, query FROM pg_stat_activity WHERE state = 'active';`

Kill hanging queries:

`SELECT pg_terminate_backend(PID);`

Find Python processes:

`ps -fA | grep python`

Kill process:

`kill -9 pid`

Create new database:

```
$ psql ericgarnick
ericgarnick=# CREATE DATABASE <db_name>;
ericgarnick=# \c <db_name>
<db_name>=# CREATE EXTENSION postgis;
```

MBTA reference: 

https://github.com/mbta/gtfs-documentation/blob/master/reference/gtfs.md
