#!/bin/bash

echo "🚀 Starting Vercel build process..."

# Set Django settings module
export DJANGO_SETTINGS_MODULE=return_mgm.settings

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!" 