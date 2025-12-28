# 📞 call-record-ingestor

A lightweight, filesystem-based ingestion pipeline for **AAC phone call recordings**.
It recursively scans directories, extracts structured metadata from filenames and AAC headers, persists records into **SQLite**, and optionally archives files into a date-based folder hierarchy.

---

## 🚀 Features

* Recursive directory scanning for `.aac` phone recordings
* Strict filename contract parsing via regex
* AAC metadata extraction (duration, bitrate, channels, sample rate)
* SQLite-backed metadata persistence
* Feature-flagged file archival (dry-run supported)
* Failure-safe logging and idempotent-friendly design
* Zero external services required

---

## 📂 Filename Convention

```
<contact>-YYYYMMDDHHMMSS.aac
```

**Example:**

```
JohnDoe-20240915183022.aac
```

---

## 🗂 Repository Structure

```
call-record-ingestor/
├── README.md
├── pyproject.toml
├── requirements.txt
├── call_record_ingestor/
│   ├── __init__.py
│   ├── config.py            # Paths, feature flags, regex
│   ├── logging_config.py    # Centralized logging setup
│   ├── database.py          # SQLite schema & access
│   ├── metadata.py          # AAC metadata extraction
│   ├── processor.py         # Core ingestion logic
│   ├── scanner.py           # Recursive directory scanning
│   └── cli.py               # CLI entry point
├── scripts/
│   └── ingest.py            # Thin wrapper for local execution
├── tests/
│   ├── __init__.py
│   ├── test_regex.py
│   ├── test_metadata.py
│   └── test_db.py
├── data/
│   ├── input/               # Sample AAC files (ignored)
│   ├── archive/             # Archived recordings (ignored)
│   └── call_records.db      # SQLite DB (ignored)
├── .gitignore
└── LICENSE
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/call-record-ingestor.git
cd call-record-ingestor
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📦 Dependencies

* Python 3.10+
* `pymediainfo` (AAC metadata extraction)
* SQLite (built-in)

> ⚠️ `pymediainfo` requires **MediaInfo** to be installed on the system.

**macOS**

```bash
brew install mediainfo
```

**Ubuntu**

```bash
sudo apt install mediainfo
```

---

## 🧠 Configuration

All configuration is centralized in `config.py`.

```python
SOURCE_DIR = Path("/data/input")
ARCHIVE_DIR = Path("/data/archive")
DB_PATH = Path("/data/call_records.db")

MOVE_FILES = False  # Feature flag (dry-run by default)

AAC_FILENAME_REGEX = r"""
(?P<contact>.*)-
(?P<year>\d{4})
(?P<month>\d{2})
(?P<day>\d{2})
(?P<hour>\d{2})
(?P<minute>\d{2})
(?P<seconds>\d{2})
\.aac$
"""
```

---

## ▶️ Usage

### CLI (Recommended)

```bash
python -m call_record_ingestor.cli
```

### Script Mode

```bash
python scripts/ingest.py
```

---

## 🗄 Database Schema

```sql
CREATE TABLE phone_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    contact TEXT NOT NULL,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    hour INTEGER,
    minute INTEGER,
    second INTEGER,
    duration_seconds REAL,
    bitrate INTEGER,
    sample_rate INTEGER,
    channels INTEGER,
    file_size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📁 Archive Layout (MOVE_FILES = true)

```
archive/
└── 2024/
    └── 09/
        ├── JohnDoe-20240915183022.aac
        └── Alice-20240915184510.aac
```

---

## 🧪 Testing

```bash
pytest
```

Test coverage includes:

* filename regex validation
* AAC metadata extraction
* SQLite insert correctness

---

## 🔐 Safety & Idempotency

* Files are **not deleted** unless `MOVE_FILES=true`
* Regex failures are logged, not fatal
* Database writes are atomic
* Designed to support future hash-based deduplication

---

## 📄 License

MIT License

---

## 👤 Author

Shrikant Sonone
