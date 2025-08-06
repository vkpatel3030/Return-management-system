# Return Management System

A Django-based web application for managing parcel returns in logistics and e-commerce operations. The system helps track and match scanned AWB (Airway Bill) numbers with uploaded delivery data to identify returned parcels.

## Features

- 🔐 **Google OAuth Authentication** - Secure login via Google accounts
- 📁 **File Upload** - Support for CSV and Excel files
- 📷 **QR Code Scanning** - Browser-based QR code scanning for AWB numbers
- 🔍 **Smart AWB Extraction** - Extracts AWB numbers from various courier tracking links
- 📊 **Data Comparison** - Matches scanned AWBs with uploaded delivery data
- 📥 **Excel Reports** - Generates matched and unmatched parcel reports
- ☁️ **Cloud Deployment** - Ready for Vercel deployment

## Technology Stack

- **Backend**: Django 4.2.15
- **Database**: SQLite
- **Authentication**: Google OAuth 2.0
- **Frontend**: Bootstrap 5, HTML5 QR Scanner
- **Deployment**: Vercel
- **Static Files**: WhiteNoise

## Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Return-management-system-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/google/redirect/
   GOOGLE_SCOPES=https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/userinfo.profile
   SECRET_KEY=your_django_secret_key
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Test the build process**
   ```bash
   python test_build.py
   ```

## Vercel Deployment

1. **Connect your repository to Vercel**

2. **Set environment variables in Vercel dashboard:**
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI` (your Vercel domain + `/google/redirect/`)
   - `GOOGLE_SCOPES`
   - `SECRET_KEY`

3. **Deploy** - Vercel will automatically handle the build process

**Note**: The deployment now uses a simplified approach without custom build scripts. Static files are served by WhiteNoise at runtime.

## Usage

1. **Login** - Use Google OAuth to authenticate
2. **Upload Data** - Upload delivery data file (CSV/Excel)
3. **Scan AWBs** - Use QR scanner to scan returned parcel AWBs
4. **Compare** - System matches scanned AWBs with uploaded data
5. **Download Reports** - Get Excel files for matched and unmatched parcels

## File Structure

```
├── core/                   # Main application
│   ├── models.py          # Data models
│   ├── views.py           # Business logic
│   ├── templates/         # HTML templates
│   └── static/            # Static files
├── auth_google/           # Google OAuth app
├── return_mgm/            # Django project settings
├── static/                # Root static files
├── build_files.sh         # Vercel build script
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

## Troubleshooting

### Vercel Deployment Issues

If you encounter "No Output Directory named 'staticfiles_build' found":

1. Ensure the `build_files.sh` script is executable
2. Check that static files exist in the project
3. Verify environment variables are set correctly
4. Run `python test_build.py` locally to test the build process

### Static Files Issues

- Ensure all templates use `{% load static %}` and `{% static 'filename' %}`
- Check that static files exist in the correct directories
- Verify `STATIC_ROOT` and `STATICFILES_DIRS` settings

## License

This project is licensed under the MIT License.