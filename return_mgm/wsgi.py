"""
WSGI config for return_mgm project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
import django
from django.core.wsgi import get_wsgi_application

# 🟢 Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'return_mgm.settings')

# ✅ Auto migrate if using SQLite in /tmp/
db_path = '/tmp/db.sqlite3'
try:
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        import subprocess
        subprocess.call(['python3', 'manage.py', 'migrate'])
except Exception as e:
    print(f"❌ Error running migrate: {e}")

# 🟢 Initialize application
try:
    django.setup()
    application = get_wsgi_application()
    print("✅ WSGI application loaded successfully")
except Exception as e:
    print(f"❌ Error loading WSGI application: {e}")
    raise

# ✅ Health check endpoint (Vercel-compatible)
def health_check(environ, start_response):
    """Simple health check for monitoring"""
    if environ.get('PATH_INFO') == '/health':
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b'OK - Django is running']
    
    # ✅ Call the actual Django application
    return application(environ, start_response)

# ✅ Expose 'app' for Vercel
app = health_check
