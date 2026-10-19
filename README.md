
# URL Shortener

A URL shortening web application built with Python and Flask. Users can submit long URLs, receive short links, and get redirected to their original destinations.

## Features

- REST API for creating short URLs
- URL validation for HTTP and HTTPS addresses
- Random six-character short codes
- SQLite database for persistent storage
- HTTP 302 redirects to original URLs
- Web interface with URL submission and copy functionality
- JSON error responses for invalid requests and unknown codes
- Automated tests using pytest

## Technologies

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- pytest
- Git

## Project Structure

```text
url-shortener/
├── templates/
│   └── index.html
├── tests/
│   └── test_app.py
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd url-shortener
```

Replace `YOUR_REPOSITORY_URL` with the actual repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/urls` | Create a short URL |
| GET | `/api/urls/<short_code>` | Retrieve saved URL information |
| GET | `/<short_code>` | Redirect to the original URL |

### Example API Request

```json
{
  "url": "https://example.com/articles/learn-python"
}
```

Send this JSON body to `POST /api/urls` with the `Content-Type: application/json` header.

## Running Tests

Run the automated test suite:

```bash
python -m pytest -v
```

The tests cover URL creation, invalid URL rejection, redirects, and unknown short codes.

## Learning Objectives

This project demonstrates practical experience with REST APIs, database persistence, input validation, HTTP status codes, automated testing, and basic web application development.
