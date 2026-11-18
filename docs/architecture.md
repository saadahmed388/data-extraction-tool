# Architecture

## 1. Purpose

The Data Extraction Tool is a desktop application for managing extraction requests and exporting data from configured Oracle environments. The application uses PyQt5 for its user interface, PostgreSQL for application metadata and configuration persistence, and `python-oracledb` for querying source databases.

This document describes the architecture visible in the current repository. It is not a deployment topology or a complete infrastructure specification.

## 2. High-level architecture

```mermaid
flowchart TB
    subgraph Desktop["Desktop application"]
        APP["app.py"]
        UI["PyQt5 MainWindow"]
        TABS["Connections · Queries · Presets<br/>Export Configurations · Service Requests · History"]
        APP --> UI
        UI --> TABS
    end

    subgraph Coordination["Application coordination layer"]
        CM["ConnectionManager"]
        QM["QueryManager"]
        PM["PresetManager"]
        ECM["ExportConfigManager"]
        EM["ExportManager"]
        HM["HistoryManager"]
    end

    subgraph Persistence["PostgreSQL persistence layer"]
        PGDM["PostgresDBManager<br/>psycopg2 connection pool"]
        PGM["PostgreSQL managers"]
        PG["PostgreSQL<br/>extraction schema"]
        PGDM --> PGM --> PG
    end

    subgraph Extraction["Extraction execution"]
        WORKER["ExtractionWorker<br/>QThread + worker object"]
        POOL["ThreadPoolExecutor<br/>up to 8 tasks"]
        ORACLE["DBClient<br/>python-oracledb connection pools"]
        CSV["Pandas DataFrame<br/>CSV files"]
        WORKER --> POOL --> ORACLE --> CSV
    end

    TABS --> Coordination
    Coordination --> Persistence
    TABS --> WORKER
    EM -. "execution inputs" .-> WORKER
    HM -. "successful run report" .-> Persistence
```

## 3. Architectural layers

### User interface

The `ui/` package contains the PyQt5 main window and the six application tabs:

- Connections
- Extraction Queries
- Presets
- Export Configurations
- Service Requests
- History

`app.py` initializes logging, creates the Qt application, loads the application icon, constructs the main window, and starts the Qt event loop.

### Application coordination

The managers in `core/managers/` coordinate application operations and provide the interface used by the UI. They delegate persistence operations to the PostgreSQL manager classes.

This separation keeps UI event handling distinct from persistence-specific operations.

### PostgreSQL persistence

The `core/postgres_managers/` package contains the PostgreSQL-facing managers. `PostgresDBManager` creates a `psycopg2` connection pool and provides connections to the persistence layer.

The application uses the PostgreSQL `extraction` schema. The repository references tables and views used for connections, queries, presets, export configurations, extraction runs, and history.

> The repository does not currently include the complete database DDL or migration scripts. The required schema objects must be provisioned separately.

### Oracle extraction

`core/oracle/db_client.py` provides the Oracle database client. It creates a connection pool for each configured source environment and exposes query and DML execution methods.

The extraction worker uses the configured connection and query definitions to execute extraction tasks.

### Execution and concurrency

`core/executors/executables.py` contains `ExtractionWorker`, a `QObject` used with a `QThread`. The worker delegates individual extraction items to a `ThreadPoolExecutor` configured with a maximum of eight workers.

This keeps the extraction operation off the main GUI thread while allowing multiple extraction items to run concurrently.

### Export generation

Query results are converted into Pandas DataFrames and written as UTF-8 CSV files. The current implementation converts returned values to strings before writing the files.

## 4. Extraction lifecycle

```mermaid
sequenceDiagram
    actor User
    participant UI as Service Requests tab
    participant Managers as Application managers
    participant Worker as ExtractionWorker
    participant Oracle as Oracle source
    participant Files as Export directory
    participant PG as PostgreSQL

    User->>UI: Select request and start extraction
    UI->>Managers: Resolve export configuration
    Managers-->>UI: Presets, queries and connections
    UI->>Worker: Start worker in QThread
    Worker->>Worker: Submit extraction items to thread pool
    loop Each extraction item
        Worker->>Oracle: Execute configured SELECT
        Oracle-->>Worker: Rows and column metadata
        Worker->>Files: Write environment CSV
    end
    Worker-->>UI: Emit completion report
    UI->>PG: Persist successful run report
    UI-->>User: Refresh history / show completion
```

The sequence describes the successful execution path. The current implementation does not persist every failure or cancellation as a completed history report.

## 5. Export directory convention

The application creates an SR-specific directory and organizes output by query class and environment:

```text
exports/
└── export_mftbcffr_<SR_NUMBER>_<DDMMYYYY>/
    └── <QUERY_CLASS>/
        ├── <ENVIRONMENT_NAME>.csv
        └── ...
```

CSV files are written with UTF-8 encoding and without a Pandas index column.

## 6. Key implementation locations

| Path | Responsibility |
|---|---|
| `app.py` | Application entry point |
| `ui/main_window.py` | Main window and dependency composition |
| `ui/` | PyQt5 screens and tabs |
| `core/managers/` | Application-level coordination |
| `core/postgres_managers/` | PostgreSQL persistence |
| `core/oracle/db_client.py` | Oracle connection and query execution |
| `core/executors/executables.py` | Background extraction and concurrent task execution |
| `core/models/data_models.py` | Pydantic data models |
| `core/exceptions/` | Application-specific exceptions |
| `config/logger_config.py` | Logging configuration |
| `utils/` | Shared UI and formatting utilities |

## 7. Current design boundaries

The following are important when interpreting the architecture:

- PostgreSQL is used for application configuration and run-history persistence; Oracle is used as the source for extracted business data.
- The UI and extraction execution are separated using Qt threading.
- The worker uses a bounded thread pool; it does not create an unbounded task per extraction item.
- The repository does not include the full PostgreSQL schema definition.
- The repository does not currently expose a comprehensive automated test suite.

For operational or production use, database provisioning, credential protection, failure-state recording, and automated tests should be documented and maintained alongside the application.
