#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to display usage
usage() {
    echo "Usage: $0 {setup|run}"
    echo
    echo "Commands:"
    echo "  setup         : Creates a virtual environment, installs dependencies, runs migrations, and runs tests."
    echo "  run [-d|--dev]  : Runs the development server. (default)"
    echo "  run [-p|--prod] : Runs the production server using gunicorn."
    exit 1
}

# Function to setup the project
setup() {
    echo "Setting up the project..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py test
    echo "Setup complete."
}

# Function to run the project
run() {
    if [ "$1" == "-p" ] || [ "$1" == "--prod" ]; then
        echo "Starting production server..."
        export DEBUG=False
        export DATABASE_URL="postgres://user:password@localhost:5432/library"
        gunicorn library.wsgi
    else
        echo "Starting development server..."
        export DEBUG=True
        export DATABASE_URL="sqlite:///db.sqlite3"
        python manage.py runserver
    fi
}

# Main script logic
if [ "$1" == "setup" ]; then
    setup
elif [ "$1" == "run" ]; then
    run "$2"
else
    usage
fi
