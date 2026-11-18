# Setup and Deployment

## 1. Prerequisites

Before setting up the application, prepare:

- A supported Python installation.
- Access to the PostgreSQL database used for application persistence.
- Access to the Oracle source environments required for extraction.
- The PostgreSQL `extraction` schema and its required tables and views.
- Network access from the desktop running the application to the configured database hosts.

The repository does not specify a pinned Python version. Use the Python version approved and validated for your target environment.

## 2. Clone the repository

```bash
git clone https://github.com/saadahmed388/data-extraction-tool.git
cd data-extraction-tool
```

## 3. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The current `requirements.txt` contains:

- `PyQt5`
- `oracledb`
- `psycopg2-binary`
- `pandas`
- `pydantic`
- `python-dotenv`

## 5. Configure PostgreSQL

Create a `.env` file in the project root:

```dotenv
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
```

Replace the placeholders with the connection details for your PostgreSQL environment.

Do not commit `.env` or real credentials. Confirm that the PostgreSQL `extraction` schema and all required tables and views have already been provisioned. The repository does not currently include a complete schema bootstrap or migration script.

## 6. Configure Oracle environments

Launch the application and configure the Oracle source connections required by your extraction workflows.

For each environment, verify:

- The DSN resolves to the intended Oracle service.
- The configured user has the required SELECT permissions.
- Any DML permissions are granted only where they are genuinely required.
- The desktop host can reach the database listener.
- Credentials are handled according to your organization's security requirements.

The application stores Oracle connection details through its PostgreSQL persistence layer. Review the security implications described in [Database Design](database-design.md) before using production credentials.

## 7. Run the application

From the repository root:

```bash
python app.py
```

The application initializes logging, creates the PyQt5 application, opens the main window, and starts the Qt event loop.

## 8. Build a Windows executable

The repository includes `Data Extraction.spec`, a PyInstaller specification file.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build using the supplied specification:

```bash
pyinstaller "Data Extraction.spec"
```

Review the generated executable and bundled resources in the PyInstaller output directory. Validate the packaged application on a clean target machine, including database connectivity, configuration access, logging paths, and export-folder permissions.

The presence of a PyInstaller specification does not by itself guarantee that the executable has been validated on every target Windows environment.

## 9. Runtime directories and files

The application uses or includes the following paths:

| Path | Purpose |
|---|---|
| `assets/` | Application icon and UI assets |
| `logs/` | Application log files |
| `exports/` | Generated extraction output |
| `data_and_config_files/` | JSON data/configuration artifacts present in the repository |

The current main-window wiring uses PostgreSQL managers as the primary persistence path. Do not assume that the JSON files are the active persistence backend without checking the relevant implementation.

## 10. Logging

Logging is configured in `config/logger_config.py`.

The current configuration includes:

- DEBUG root logging level.
- Console logging.
- A rotating file handler at `logs/logs.log`.
- A maximum log file size of approximately 5 MB.
- Five backup log files.

Ensure the application has permission to create and write to the configured log directory.

## 11. Operational checks

Before using the application for a real extraction:

1. Confirm PostgreSQL connectivity.
2. Confirm that required configuration records are available.
3. Test each Oracle connection independently.
4. Verify that the selected query is valid for the target environment.
5. Confirm that the export destination is writable and has sufficient disk space.
6. Run a small, known extraction and compare its output with an independently verified result.
7. Confirm that the successful run appears in the application's history.

## 12. Troubleshooting checklist

| Symptom | Checks |
|---|---|
| Application cannot connect to PostgreSQL | Check `.env`, `DATABASE_URL`, network access, credentials, and database availability |
| Oracle connection fails | Check DSN, listener/network access, credentials, and database permissions |
| Query fails | Validate SQL against the intended Oracle environment and check object privileges |
| CSV is not created | Check extraction logs, destination permissions, available disk space, and query results |
| History is not updated | Check the successful completion path and PostgreSQL persistence availability |
| Packaged executable fails | Rebuild, inspect PyInstaller output, and test required assets and runtime dependencies |

For production deployment, use environment-specific configuration, controlled database permissions, secure secret storage, and a repeatable release process.
