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

@google_login_required
def home(request):
    return render(request, 'home.html')


def upload_file(request):
    if request.method == 'POST':
        # Your file processing logic here...
        
        # Instead of passing raw dictionary data, convert to list format
        processed_data = []
        columns = ['AWB', 'Date', 'Status']  # Your actual columns
        
        for row in raw_data:  # raw_data is your original dictionary data
            row_list = []
            for col in columns:
                row_list.append(row.get(col, ''))
            processed_data.append(row_list)
        
        context = {
            'data': processed_data,
            'columns': columns,
            'success_msg': 'File uploaded successfully!'
        }
        return render(request, 'upload.html', context)
    
    return render(request, 'upload.html')


def scan_awb(request):
    return render(request, 'scan.html')


def save_scan(request):
    if request.method == 'POST':
        scanned_data = request.POST.get('scanned_data', '')
        new_awbs = set(awb.strip() for awb in scanned_data.replace('\n', ',').split(',') if awb.strip())

        file_path = os.path.join(settings.MEDIA_ROOT, 'scanned_awbs.txt')
        existing_awbs = set()

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    aw = line.strip()
                    if aw:
                        existing_awbs.add(aw)

        combined_awbs = existing_awbs.union(new_awbs)

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
             if os.path.isfile(os.path.join(upload_folder, f))]
    if not files:
        return None

    return max(files, key=os.path.getctime)


def extract_awb_from_url(url):
    if not isinstance(url, str):
        return ''
    patterns = [
        r'trackingId=([A-Z0-9]+)',
        r'refNum=([A-Z0-9]+)',
        r'trackid=([0-9]+)',
        r'/([A-Z0-9]{10,})$',
        r'/package/([0-9]+)',
    ]
    for pattern in patterns:
        m = re.search(pattern, str(url))
        if m:
            return m.group(1)
    return url.strip()


def compare_data(request):
    try:
        latest_file = get_latest_uploaded_file()
        if not latest_file:
            return HttpResponse("No file uploaded.")

        ext = os.path.splitext(latest_file)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(latest_file, dtype=str)
        else:
            df = pd.read_excel(latest_file, engine='openpyxl', dtype=str)

        df = df.applymap(lambda x: str(x).strip())

        scanned_file = os.path.join(settings.MEDIA_ROOT, 'scanned_awbs.txt')
        if not os.path.exists(scanned_file):
            return HttpResponse("No scanned AWB data found.")

        with open(scanned_file, 'r') as f:
            scanned_awbs = [line.strip() for line in f if line.strip()]
        scanned_set = set(scanned_awbs)

        if 'Tracking Link' in df.columns:
            df['__awb__'] = df['Tracking Link'].apply(extract_awb_from_url)
        elif 'AWB Number' in df.columns:
            df['__awb__'] = df['AWB Number'].astype(str).str.strip()
        else:
            return HttpResponse("AWB column not found.")

        df['Matched'] = df['__awb__'].isin(scanned_set)

        matched_df = df[df['Matched']].drop(columns=['Matched'])
        unmatched_df = df[~df['Matched']].drop(columns=['Matched'])

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
