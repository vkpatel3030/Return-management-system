#!/bin/bash

echo "🚀 Starting Vercel build..."

# Set Django settings
export DJANGO_SETTINGS_MODULE=return_mgm.settings

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!" 