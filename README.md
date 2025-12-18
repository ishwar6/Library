# Library Management System

This is a Django-based Library Management System that provides a RESTful API for managing books and loans.

## Features

- **User Management:** User registration and administration.
- **JWT Authentication:** Secure API access using JSON Web Tokens.
- **Book Management:** Add, update, delete, and list books.
- **Loan Management:** Borrow and return books.
- **API Documentation:** Interactive API documentation using Swagger UI.
- **Filtering and Pagination:** Filter books by availability and search by title or author. Paginated results for all list endpoints.
- **CORS:** Cross-Origin Resource Sharing enabled for easy integration with frontend applications.
- **Docker Support:** Dockerfile included for easy containerization.
- **Heroku Ready:** Includes a `Procfile` for easy deployment to Heroku.

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)
- Heroku CLI (optional)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd library-management-system
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    - Copy the example environment file:
      ```bash
      cp .env.example .env
      ```
    - Edit `.env` and set your configuration:
      - `SECRET_KEY`: Generate a secure key (see `.env.example` for instructions)
      - `DEBUG`: Set to `True` for development, `False` for production
      - `DATABASE_URL`: For local development with SQLite, use `sqlite:///db.sqlite3`
        For PostgreSQL, use `postgresql://user:password@localhost:5432/library`
      - `ALLOWED_HOSTS`: Comma-separated list (e.g., `localhost,127.0.0.1`)
      - `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins (optional for development)

    **Note:** The application will work with default values for local development, but you should set a proper `SECRET_KEY` for production.

5.  **Set up the database:**

    - For SQLite (default): No setup needed, database file will be created automatically.
    - For PostgreSQL:
      - Make sure you have a PostgreSQL server running.
      - Create a database (e.g., `library`).
      - Update `DATABASE_URL` in your `.env` file.

6.  **Run the database migrations:**

    ```bash
    python manage.py migrate
    ```

7.  **Create a superuser (optional, for admin access):**

    ```bash
    python manage.py createsuperuser
    ```

8.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

### API Documentation

The API documentation is available at `http://127.0.0.1:8000/swagger/`.

### Running with Docker

1.  **Build the Docker image:**

    ```bash
    docker build -t library-management .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 library-management
    ```

### Running Tests

Run all tests:

```bash
python manage.py test
```

Run tests for a specific app:

```bash
python manage.py test api
```

Run tests with verbose output:

```bash
python manage.py test --verbosity=2
```

**Test Coverage:**
The test suite includes:

- Unit tests for models (User, Book, Loan)
- Unit tests for serializers
- ViewSet tests for User, Book, and Loan endpoints
- Integration tests for borrowing/returning workflow
- Permission and authentication tests

## Deployment to Heroku

1.  **Create a Heroku app:**

    ```bash
    heroku create
    ```

2.  **Add a PostgreSQL addon:**

    ```bash
    heroku addons:create heroku-postgresql:hobby-dev
    ```

3.  **Push the code to Heroku:**

    ```bash
    git push heroku main
    ```

4.  **Set environment variables on Heroku:**

    ```bash
    heroku config:set SECRET_KEY=your-secret-key-here
    heroku config:set DEBUG=False
    heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
    heroku config:set CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
    heroku config:set SECURE_SSL_REDIRECT=True
    heroku config:set SESSION_COOKIE_SECURE=True
    heroku config:set CSRF_COOKIE_SECURE=True
    ```

    The `DATABASE_URL` is automatically set by Heroku when you add the PostgreSQL addon.

5.  **Run the migrations on Heroku:**

    ```bash
    heroku run python manage.py migrate
    ```

6.  **Create a superuser on Heroku:**
    ```bash
    heroku run python manage.py createsuperuser
    ```

## Troubleshooting

### Common Issues

**Issue: `SECRET_KEY` not set error**

- **Solution:** Copy `.env.example` to `.env` and set a `SECRET_KEY`, or the application will use a default key (not recommended for production).

**Issue: Database connection errors**

- **Solution:** Check your `DATABASE_URL` in `.env`. For SQLite, ensure the path is correct. For PostgreSQL, verify credentials and that the database exists.

**Issue: CORS errors when accessing API from frontend**

- **Solution:** Set `CORS_ALLOWED_ORIGINS` in `.env` with your frontend URL, or ensure `DEBUG=True` for development.

**Issue: 401 Unauthorized errors**

- **Solution:** Ensure you're sending the JWT token in the `Authorization` header: `Bearer <your-token>`. Get a token from `/api/token/` endpoint.

**Issue: Admin panel not accessible**

- **Solution:** Create a superuser with `python manage.py createsuperuser` and ensure you're logged in.

**Issue: Tests failing**

- **Solution:** Ensure migrations are up to date: `python manage.py migrate`. Check that the test database can be created.

### Getting Help

- Check the API documentation at `/swagger/` for endpoint details
- Review the test files in `api/tests.py` for usage examples
- Check Django logs for detailed error messages
