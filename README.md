# Server Inventory Manager

A lightweight IT server inventory application built with FastAPI. The application provides a Bootstrap-based web interface and a JSON API for creating, viewing, editing, and deleting server records. Data is stored locally in SQLite through SQLAlchemy.

## Technologies

- FastAPI
- SQLite
- SQLAlchemy
- Jinja2
- Bootstrap 5

## Installation

### 1. Clone or download the project

Open a terminal in the project directory:

```text
cd FastAPI-InventoryManager
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the application

```bash
uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser. The SQLite database file, `inventory.db`, and its initial example records are created automatically when the application starts.

## Main Routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Display the server inventory |
| `GET` | `/servers` | Display the server inventory |
| `POST` | `/add` | Add a server from the web form |
| `GET` | `/edit/{server_id}` | Display the edit form for a server |
| `POST` | `/edit/{server_id}` | Update a server |
| `POST` | `/delete/{server_id}` | Delete a server |
| `POST` | `/servers` | Add a server through the JSON API |

## Project Structure

```text
.
|-- main.py
|-- requirements.txt
|-- templates/
|   |-- index.html
|   `-- edit.html
`-- inventory.db        # Created automatically at runtime
```
