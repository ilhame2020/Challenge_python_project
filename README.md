
## Students Flask App

A small, self-contained Flask application to manage student records (name, age, grade). This project was converted from a command-line script and adds a web UI, a minimal REST endpoint, and a file upload importer for CSV-like files.

Contents
- `app.py` — Flask application and route handlers.
- `students.txt` — simple CSV-like data store that persists student records.
- `templates/` — Jinja2 templates for UI: listing, adding, failing, and uploading.
- `requirements.txt` — Python dependencies.

Key features
- Web UI to list and add students.
- JSON API endpoint: `GET` and `POST` at `/api/students`.
- Upload a CSV-like file (one `Name,Age,Grade` per line) to merge students into the list.
- Simple persistence to `students.txt` (human-readable, easy to edit).

---

**Requirements**
- Python 3.8+ (the project was validated with Python 3.13).
- `pip` to install dependencies.

## Installation (PowerShell)

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running the application

Start the Flask server:

```powershell
python app.py
```

By default the app listens on `http://127.0.0.1:5000`.

Open your browser and visit `http://127.0.0.1:5000` to use the web UI.

## Usage

- List students: use the home page. The page shows average grade, best student, and an age-group summary.
- Add a student: click `Add` in the navigation bar and submit the form.
- Upload a file: click `Upload` and choose a text or CSV file where each line is `Name,Age,Grade`.
- Save: the app auto-saves when adding or uploading; you can also click `Save` on the UI to write current in-memory data to `students.txt`.

### Upload file format

The upload accepts plain text files where each non-empty line contains exactly three comma-separated values:

```
Name,Age,Grade
```

Example:

```
Lina,18,16.5
Omar,20,14.0
```

Lines that are malformed, missing fields, or that contain non-numeric values for age/grade are skipped and reported on upload.

## API

GET students (JSON):

```powershell
curl http://127.0.0.1:5000/api/students
```

POST a student (JSON):

```powershell
curl -X POST http://127.0.0.1:5000/api/students -H "Content-Type: application/json" -d '{"name":"Ali","age":19,"grade":12.5}'
```

Response codes:
- `200` — successful GET
- `201` — successful POST (student created)
- `400` — bad request (invalid payload)

## Data persistence

Records are stored in `students.txt` in the project root using a simple CSV-like format. The app loads this file on start and writes to it when you add students or upload a file. You can edit `students.txt` manually if needed, but keep each line as `Name,Age,Grade`.

## Development notes

- The simple design intentionally avoids a database to keep the project lightweight and easy to run.
- For production or multi-user usage, move to a proper database (SQLite/Postgres) and add authentication.

## Troubleshooting

- If the server does not start, check for errors in the terminal where you ran `python app.py`.
- Make sure you have activated the virtual environment and installed dependencies.
- If file uploads fail for large files, the upload limit is set to 1MB by default; you can adjust `app.config['MAX_CONTENT_LENGTH']` in `app.py`.

## Next steps (suggested)

- Add unit tests for the parsing logic in `app.py`.
- Add CSRF protection for forms (Flask-WTF) if deploying publicly.
- Add Dockerfile for reproducible deployment.

---

If you want, I can also:
- Start the development server in a terminal here so you can test uploads interactively.
- Add tests for the CSV importer and run them.
- Add a Dockerfile and a simple `Makefile`/`task` to simplify running and testing.
