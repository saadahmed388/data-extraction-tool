
# Data Extraction Tool

> A Python-based desktop application for managing, executing, and exporting environment-specific data extraction workflows across multiple Oracle database environments.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![Oracle](https://img.shields.io/badge/Business%20Backend-Oracle-red)
![PostgreSQL](https://img.shields.io/badge/Application%20Backend-PostgreSQL-336791)
![License](https://img.shields.io/badge/License-Apache--2.0-green)

## Overview

The **Data Extraction Tool** is a Python-based desktop application designed to simplify and standardize data extraction workflows across multiple Oracle environments.

It provides a centralized interface for managing database connections, maintaining reusable SQL queries, configuring extraction presets, executing extraction workflows, and generating structured outputs.

Version 2.0 introduces PostgreSQL as the centralized application persistence backend, replacing the previous JSON-based persistence approach.

## Key Features

### 🗄️ Environment-Aware Database Connectivity
- Manage multiple Oracle database environments.
- Maintain environment-specific connection configurations.
- Use Oracle connection pooling for efficient database access.
- Execute extraction queries against selected environments.

### 🔍 Query Management
- Create, update, and organize reusable SQL queries.
- Maintain query classifications and metadata.
- Associate queries with extraction environments.

### ⚙️ Presets & Export Configurations
- Create reusable extraction presets.
- Combine queries and environments into configurable workflows.
- Organize presets into named export configurations.
- Associate Service Requests with their respective extraction configurations.

### 📤 Extraction & Export
- Execute configured extraction workflows.
- Run extraction operations in background threads.
- Generate structured output files.
- Capture extraction execution details and results.

### 📚 Persistent History
- Maintain Service Request and extraction records.
- Persist execution reports and extraction metadata.
- Retrieve historical execution information through the application interface.

## Architecture

The application follows a **three-layer architecture**, separating presentation, application logic, and data infrastructure.

```mermaid
flowchart TB
    U[User]

    subgraph L1["1. Presentation Layer"]
        UI[PyQt5 Desktop UI]
        V[Connections | Queries | Presets]
        W[Export Configurations | Service Requests | History]
    end

    subgraph L2["2. Application Layer"]
        M[Application Managers]
        D[Data Models and Validation]
        E[Extraction Workflow and Orchestration]
        X[Background Execution]
    end

    subgraph L3["3. Data / Infrastructure Layer"]
        OC[Oracle DB Client]
        OP[Oracle Connection Pool]
        PM[PostgreSQL Managers]
        PG[PostgreSQL Connection Pool]
    end

    ORA[(Oracle Database<br/>Business Data)]
    POST[(PostgreSQL Database<br/>Application Data)]
    FS[(Export Files)]

    U --> UI
    UI --> V
    UI --> W
    V --> M
    W --> M
    M --> D
    M --> E
    E --> X
    X --> OC
    OC --> OP
    OP --> ORA
    M --> PM
    PM --> PG
    PG --> POST
    X --> FS
```

### Layer Responsibilities

| Layer | Responsibility |
|---|---|
| **Presentation** | PyQt5 interface, application views, user interactions, and visualization of extraction results. |
| **Application** | Business workflows, application managers, configuration coordination, data validation, and extraction orchestration. |
| **Data / Infrastructure** | Oracle connectivity, PostgreSQL persistence, connection pooling, and database access operations. |

### Database Architecture

The application uses two databases with clearly separated responsibilities:

**PostgreSQL — Application Backend**
- Sole active persistence backend.
- Stores database connection configurations and metadata.
- Maintains queries, presets, and export configurations.
- Persists Service Request records and extraction history.

**Oracle — Business Backend**
- Source of business and operational data.
- Executes configured SQL extraction queries.
- Supports multiple database environments through independent connection pools.

This separation keeps application metadata independent of the business databases being queried.

## Component Responsibilities

| Component | Responsibility |
|---|---|
| `ui/` | PyQt5 views and user interactions. |
| `core/managers/` | Application-level managers coordinating configurations, queries, presets, exports, and history. |
| `core/postgres_managers/` | PostgreSQL persistence operations for application entities. |
| `core/postgres_managers/db_manager.py` | PostgreSQL connection pool and connection lifecycle management. |
| `core/db_client.py` | Oracle database connectivity, connection pooling, and SQL execution. |
| `core/data_models.py` | Pydantic models for structured application operation payloads. |
| `core/exceptions.py` | Application-specific exception definitions. |
| `utilities/` | Background extraction workers, logging, UI utilities, and supporting components. |
| `config/` | Application configuration. |
| `assets/` | Application icons and graphical resources. |
| `logs/` | Application execution and diagnostic logs. |
| `app.py` | Application entry point and initialization. |

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| PyQt5 | Desktop interface |
| PostgreSQL | Application persistence |
| psycopg2 | PostgreSQL connectivity and pooling |
| python-oracledb | Oracle connectivity and pooling |
| Pydantic | Data validation and structured payloads |
| Pandas | Dataset processing |
| PyInstaller | Desktop application packaging |

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL database
- Access to the required Oracle environments
- Valid database credentials

### Clone Repository

```bash
git clone https://github.com/saadahmed388/data-extraction-tool.git
cd data-extraction-tool
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Activate on Windows:

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure PostgreSQL

Configure the PostgreSQL connection using the `DATABASE_URL` environment variable.

```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

Ensure the required application schema and database objects are provisioned.

### Run Application

```bash
python app.py
```

Configure the required Oracle environments through the application before executing extraction workflows.

## Project Status

**v2.0.0 — PostgreSQL Backend Integration**

Introduces centralized PostgreSQL persistence, dedicated persistence managers, structured Pydantic payloads, and pooled database connectivity.

Further development includes UI refinement, completion of extraction history, and continued improvements to application reliability and maintainability.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Author

**Saad Ahmed**

[GitHub](https://github.com/saadahmed388)
