#!/bin/bash

echo "🔧 Running build steps..."


# Run database migrations
python3 manage.py migrate

echo "✅ Build complete!"
