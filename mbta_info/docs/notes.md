Finding hanging queries:

`SELECT pid, query FROM pg_stat_activity WHERE state = 'active';`

Killing hanging queries:

`SELECT pg_terminate_backend(PID);`
