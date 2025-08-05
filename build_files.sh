#!/bin/bash

echo "🔧 Running build steps..."

# Collect static files
python3 manage.py collectstatic --noinput

# Run database migrations
python3 manage.py migrate

echo "✅ Build complete!"
