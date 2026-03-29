# Helpful commands

## Docker compose

## Grafana cont

## Python

## PostgreSQL

After joining db:
```sh
su - postgres

psql -U sayso_user -d sayso_db
```

Show databases:
```sql
\l
||
SELECT datname FROM sayso_db
```

Connect to DB:
```sql
\c DB_NAME
```

Show tables:
```sql
\dt
```