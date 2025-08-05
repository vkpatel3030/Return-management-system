#!/usr/bin/env python3
"""
Test script to verify the build process works correctly
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'return_mgm.settings')
django.setup()

from django.core.management import execute_from_command_line

def test_static_collection():
    """Test static file collection"""
    print("🧪 Testing static file collection...")
    
    # Create staticfiles_build directory
    static_build_dir = project_dir / 'staticfiles_build'
    static_build_dir.mkdir(exist_ok=True)
    
    # Run collectstatic
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--verbosity=2'])
    
    # Check if files were collected
    static_dir = static_build_dir / 'static'
    if static_dir.exists():
        print(f"✅ Static files collected successfully to {static_dir}")
        files = list(static_dir.rglob('*'))
        print(f"📁 Found {len(files)} static files")
        for file in files[:5]:  # Show first 5 files
            print(f"   - {file.relative_to(static_dir)}")
    else:
        print("❌ Static files directory not created")
        return False
    
    return True

def test_migrations():
    """Test database migrations"""
    print("\n🧪 Testing database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Starting build test...")
    
    success = True
    success &= test_static_collection()
    success &= test_migrations()
    
    if success:
        print("\n🎉 All tests passed! Build should work on Vercel.")
    else:
        print("\n💥 Some tests failed. Please fix issues before deploying.")
        sys.exit(1) 