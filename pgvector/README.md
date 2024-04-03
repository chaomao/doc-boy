# Chroma to PGvector conversion script

## Instructions

1. Launch PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension installed. You can do that by running `docker-compose up` or manually
2. Create a new database
    ```
    echo "CREATE DATABASE gitlabhq_development_embedding;" | psql -h localhost -p 5433 -Upostgres
    ```
3. Create tanuki_bot table
   ```
   psql -h localhost -p 5433 -Upostgres gitlabhq_development_embedding < pgvector/structure.sql
   ```
4. You should be able to use psql
   ```
   psql -h localhost -p 5433 -Upostgres gitlabhq_development_embedding
   ```
5. Migrate data from Chroma to PostgreSQL
   ```
   cd pgvector
   PG_PORT=5433 python chroma_to_pg.py
   ```
