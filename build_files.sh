#!/bin/bash

echo "🔧 Running build steps..."

# Create the staticfiles_build directory if it doesn't exist
mkdir -p staticfiles_build

# Set Django settings module
export DJANGO_SETTINGS_MODULE=return_mgm.settings

# Collect static files with verbose output
echo "📁 Collecting static files..."
python3 manage.py collectstatic --noinput --verbosity=2

# Run database migrations
echo "🗄️ Running database migrations..."
python3 manage.py migrate --noinput

# List the contents of staticfiles_build to verify
echo "📋 Contents of staticfiles_build:"
ls -la staticfiles_build/

echo "✅ Build complete!"
