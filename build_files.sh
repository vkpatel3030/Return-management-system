#!/bin/bash

echo "🔧 Running build steps..."

python3 manage.py makemigrations

# Run database migrations
python3 manage.py migrate

echo "✅ Build complete!"
