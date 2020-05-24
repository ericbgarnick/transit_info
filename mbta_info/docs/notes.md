#### Find hanging queries:

`SELECT pid, query FROM pg_stat_activity WHERE state = 'active';`

---

#### Kill hanging queries:

`SELECT pg_terminate_backend(PID);`

---

#### Find Python processes:

`ps -fA | grep python`

---

#### Kill process:

`kill -9 pid`

---

#### Create new database:

```
$ psql ericgarnick
ericgarnick=# CREATE DATABASE <db_name>;
ericgarnick=# \c <db_name>
<db_name>=# CREATE EXTENSION postgis;
```

---

#### MBTA reference: 

https://github.com/mbta/gtfs-documentation/blob/master/reference/gtfs.md

---

#### Adding a new data sheet

1. Update config_development.yaml `mbta_data.files` with a mapping from the table name to the file name, placed in the list after any files it depends on
2. Create a new db model in flaskr/models.py
3. Create a marshmallow schema in flaskr/schemas.py
4. Add new table name to test_loader::test_init `table_names` list, maintaining the order set in config_development.yaml
5. Add unit tests for the schema (see existing schema tests for examples)

---

#### Dev env setup

Requirements:
- Python 3.7
- RabbitMQ: 
  - install: `sudo apt-get install rabbitmq-server`
  - run: `sudo service rabbitmq-server start/stop`
  - check: `sudo service rabbitmq-server status`
- Celery:
  - Foreground worker (with beat): `celery -A mbta_info.flaskr.celery.app worker -l info -B`
  - Background worker: 
    - `celery multi <cmd> w1 -A mbta_info.flaskr.celery.app -l info`
    where `<cmd>` is `start`, `restart`, `stop`, `stopwait`

---

#### Docker

- Create celery worker image

    `sudo docker build --tag worker:1.0 .`

- Start containers

    `sudo docker-compose up -d`

- Run command in a container
    - `sudo docker container exec -it <container> <command>`
    - `<command>` := `/bin/sh` for interactive shell

---

#### Search for an apt package
- `apt-cache search <package>`