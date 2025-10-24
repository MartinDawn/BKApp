# BKApp

BKApp is a Django-based web application project. This project provides a backend API and web interface for managing and interacting with data stored in a SQLite database.

## Features
- Django web framework
- SQLite database (default for development)
- Modular project structure
- Ready for deployment (Procfile and runtime.txt included)

## Project Structure
```
myproject/
    __init__.py
    adapters.py
    asgi.py
    settings.py
    urls.py
    views.py
    wsgi.py
manage.py
db.sqlite3
requirements.txt
Procfile
runtime.txt
```

## Getting Started

### Prerequisites
- Python 3.12 or compatible version
- pip (Python package manager)

### Installation
1. Clone the repository:
   ```powershell
   git clone <repository-url>
   cd BKApp
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```powershell
   python manage.py migrate
   ```
4. Start the development server:
   ```powershell
   python manage.py runserver
   ```

### Deployment
- The project includes a `Procfile` and `runtime.txt` for deployment on platforms like Heroku.

## License
This project is licensed under the MIT License.
