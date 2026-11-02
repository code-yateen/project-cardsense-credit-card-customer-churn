# PostgreSQL analytics phase

This folder contains the next project phase's database schema and descriptive business queries. It uses the 21-column cleaned extract; the source's precomputed `Naive_Bayes_Classifier*` outputs are excluded. A PostgreSQL 18.6 runtime is downloaded into the Git-ignored `.pg_runtime/` folder, but its database cluster is not initialized and the SQL has not been run against a database.

## Initialize, load, and analyze

From the project root, run:

```powershell
.\scripts\run_postgres_phase.ps1
```

The script initializes a local cluster in `.pgdata/`, binds the server to `127.0.0.1:5433`, creates `cardsense_db`, applies the schema, loads the cleaned CSV, and runs the analysis queries. It creates a random local database password and writes the connection URL to the Git-ignored `.env` file. PostgreSQL remains local to this project and does not install a Windows service. The server stays running after the script completes; stop it with `pg_ctl -D .pgdata stop` from a PowerShell session with `.pg_runtime\Library\bin` on `PATH`.

Keep credentials in environment variables; do not commit passwords. The loader creates a temporary staging table and upserts by `clientnum`, so rerunning it does not duplicate customers. The SQL schema has basic domain checks and does not replace upstream data-quality review.

The analysis queries are descriptive and do not establish causation or predict future churn.
