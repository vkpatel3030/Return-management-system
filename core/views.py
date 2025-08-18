import os
import pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from .models import UploadedFile
from django.core.files.storage import FileSystemStorage
import re
from auth_google.decorators import google_login_required
import uuid
import time
from io import BytesIO



uploaded_data_df = pd.DataFrame()
scanned_awb_list = []

@google_login_required
def home(request):
    return render(request, 'home.html')

def upload_file(request):
    """
    Supabase compatible file upload:
    - Read CSV / Excel using pandas
    - Upload as Excel buffer to Supabase with UNIQUE filename (timestamp prefix)
    - Save simple file reference in DB
    - Render uploaded data as HTML table using df.to_dict()
    """
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']              # Uploaded by user

        # 1) Read CSV / Excel
        ext = os.path.splitext(file.name)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, engine='openpyxl')

        uploaded_data_df = df.copy()

        # 2) Write DF to Bytes buffer
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # 3) Create unique file name to avoid 409 Duplicate (use timestamp)
        import time
        bucket_name = "uploads"
        unique_name = f"{int(time.time())}_{file.name}"
        file_path = f"uploaded/{unique_name}"

        # 4) Upload to Supabase bucket
        supabase.storage.from_(bucket_name).upload(
            file_path,
            excel_buffer.read(),
            {
                "content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        )

        # 5) Save file reference in DB model
        UploadedFile.objects.create(file=file)

        # 6) Return HTML table using upload.html template
        return render(request, 'upload.html', {
            'data': df.to_dict(orient='records'),
            'columns': df.columns
        })

    # If GET request -> show empty or last uploaded table
    return render(request, 'upload.html', {
        'data': uploaded_data_df.to_dict(orient='records') if not uploaded_data_df.empty else [],
        'columns': uploaded_data_df.columns if not uploaded_data_df.empty else []
    })


def scan_awb(request):
    return render(request, 'scan.html')

def save_scan(request):
    if request.method == 'POST':
        scanned_data = request.POST.get('scanned_data', '')
        new_awbs = set(awb.strip() for awb in scanned_data.replace('\n', ',').split(',') if awb.strip())

        file_path = os.path.join(settings.MEDIA_ROOT, 'scanned_awbs.txt')
        existing_awbs = set()

        # Read old AWB numbers if file exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if ',' in line:
                            existing_awbs.update(x.strip() for x in line.split(','))
                        else:
                            existing_awbs.add(line)

        # Combine old and new without duplicates
        combined_awbs = existing_awbs.union(new_awbs)

        # Save final combined list back to file
        with open(file_path, 'w') as f:
            for awb in combined_awbs:
                f.write(f"{awb}\n")

        return redirect('compare')

    return HttpResponse("Invalid Request", status=400)

def get_latest_uploaded_file():
    upload_folder = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_folder):
        return None

    files = [os.path.join(upload_folder, f) for f in os.listdir(upload_folder)
             if os.path.isfile(os.path.join(upload_folder, f)) and f.endswith(('.xlsx', '.xls', '.csv'))]
    if not files:
        return None

    latest_file = max(files, key=os.path.getctime)
    return latest_file

# 🎯 AWB Extractor from any tracking link
def extract_awb_from_url(url):
    if not isinstance(url, str):
        return ''
     
    patterns = [
        r'trackingId=([A-Z0-9]+)',              # Shadowfax
        r'refNum=([A-Z0-9]+)',                  # Meesho
        r'trackid=([0-9]+)',                    # XpressBees
        r'/([A-Z0-9]{10,})$',                   # Valmo, fallback
        r'/package/([0-9]+)',                   # Delhivery
    ]
    for pattern in patterns:
        match = re.search(pattern, str(url))
        if match:
            return match.group(1)
    return url.strip()

def compare_data(request, latest_uploaded_path=None):
    try:
        bucket_name = "uploads"

        if latest_uploaded_path:
            # જો upload_file માંથી path મળ્યું છે તો એ જ file લેવી
            latest_file_name = latest_uploaded_path
        else:
            # Supabase માંથી latest file fetch કરવી
            files_list = supabase.storage.from_(bucket_name).list("uploaded")
            if not files_list:
                return HttpResponse("No file uploaded in Supabase.")
            latest_file_info = sorted(files_list, key=lambda x: x['created_at'], reverse=True)[0]
            latest_file_name = f"uploaded/{latest_file_info['name']}"

        # Download file
        file_response = supabase.storage.from_(bucket_name).download(latest_file_name)
        if not file_response:
            return HttpResponse("Error downloading file from Supabase.")

        import io
        file_bytes = io.BytesIO(file_response)
        ext = os.path.splitext(latest_file_name)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_bytes, dtype=str, header=6)
        else:
            df = pd.read_excel(file_bytes, engine='openpyxl', dtype=str, header=6)

        df = df.applymap(lambda x: str(x).strip())

        # Load scanned AWBs
        scanned_file = os.path.join(settings.MEDIA_ROOT, 'scanned_awbs.txt')
        if not os.path.exists(scanned_file):
            return HttpResponse("No scanned AWB data found.")

        with open(scanned_file, 'r') as f:
            content = f.read()
            if ',' in content:
                scanned_awbs = [awb.strip() for awb in content.split(',') if awb.strip()]
            else:
                scanned_awbs = [awb.strip() for awb in content.strip().split('\n') if awb.strip()]
        scanned_awbs_set = set([x.strip() for x in scanned_awbs if x])

        # AWB extraction
        if 'Tracking Link' in df.columns:
            df['__awb__'] = df['Tracking Link'].apply(extract_awb_from_url)
        elif 'AWB Number' in df.columns:
            df['__awb__'] = df['AWB Number'].astype(str).str.strip()
        else:
            return HttpResponse("AWB column not found.")

        # Match
        df['Matched'] = df['__awb__'].isin(scanned_awbs_set)
        matched_df = df[df['Matched']].drop(columns=['Matched'])
        unmatched_df = df[~df['Matched']].drop(columns=['Matched'])

        # Save local results
        matched_df.to_excel(os.path.join(settings.MEDIA_ROOT, 'matched.xlsx'), index=False)
        unmatched_df.to_excel(os.path.join(settings.MEDIA_ROOT, 'unmatched.xlsx'), index=False)

        request.session['matched'] = matched_df.to_dict(orient='records')
        request.session['unmatched'] = unmatched_df.to_dict(orient='records')

        return render(request, 'result.html', {
            'matched_count': len(matched_df),
            'unmatched_count': len(unmatched_df)
        })

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")
def download_matched(request):
    matched = pd.DataFrame(request.session.get('matched', []))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=matched.xlsx'
    matched.to_excel(response, index=False, engine='openpyxl')
    return response

def download_unmatched(request):
    unmatched = pd.DataFrame(request.session.get('unmatched', []))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=unmatched.xlsx'
    unmatched.to_excel(response, index=False, engine='openpyxl')
    return response

def google_login(request):
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "https://return-management-system.vercel.app/google/redirect/")],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/userinfo.profile").split()
        )

        flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://return-management-system.vercel.app/google/redirect/")
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        request.session['state'] = state
        return redirect(auth_url)
    except Exception as e:
        # Debug માટે error show કરો
        return render(request, 'error.html', {'error': str(e)})

def google_redirect(request):
    try:
        state = request.session.get('state')

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "https://return-management-system.vercel.app/google/redirect/")],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/userinfo.profile").split(),
            state=state
        )
        flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://return-management-system.vercel.app/google/redirect/")

        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        request.session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        return redirect('home')
    except Exception as e:
        # Debug માટે error show કરો
        return render(request, 'error.html', {'error': str(e)})

def drive_list(request):
    try:
        from google.oauth2.credentials import Credentials

        creds_data = request.session.get('credentials')
        if not creds_data:
            return redirect('google_login')

        creds = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=creds_data['client_id'],
            client_secret=creds_data['client_secret'],
            scopes=creds_data['scopes'],
        )

        headers = {"Authorization": f"Bearer {creds.token}"}
        response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers)
        files = response.json().get("files", [])

        return render(request, "drive_files.html", {"files": files})
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})