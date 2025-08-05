"""
WSGI config for return_mgm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# 🟢 Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'return_mgm.settings')

# 🟢 Error handling for better debugging
try:
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
