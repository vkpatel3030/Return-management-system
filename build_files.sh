#!/bin/bash

# Apply database migrations (if needed)
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
