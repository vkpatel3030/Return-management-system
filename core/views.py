import os
import pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
import uuid
import re

def home(request):
    return render(request, 'home.html')

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        ext = os.path.splitext(file.name)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, engine='openpyxl')

        upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_path, exist_ok=True)

        unique_name = f"{uuid.uuid4()}_{file.name}"
        file_path = os.path.join(upload_path, unique_name)

        with open(file_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        # Show preview
        return render(request, 'upload.html', {
            'data': df.to_dict(orient="records"),
            'columns': df.columns,
            'success_msg': 'File uploaded successfully!',
            'uploaded_file': file_path
        })

    return render(request, 'upload.html')

def scan_awb(request):
    return render(request, 'scan.html')

def save_scan(request):
    if request.method == 'POST':
        scanned_data = request.POST.get('scanned_data', '')
        new_awbs = set(a.strip() for a in scanned_data.replace('\n', ',').split(',') if a.strip())

        txt_path = os.path.join(settings.MEDIA_ROOT, 'scanned_awbs.txt')
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        if os.path.exists(txt_path):
            with open(txt_path, 'r') as f:
                existing = {line.strip() for line in f if line.strip()}
        else:
            existing = set()

        combined = existing.union(new_awbs)

        with open(txt_path, 'w') as f:
            for aw in combined:
                f.write(f"{aw}\n")

        return redirect('compare')

    return HttpResponse("Invalid Request", status=400)

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

def get_latest_uploaded_file():
    upload_folder = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_folder):
        return None
    files = [os.path.join(upload_folder, f) for f in os.listdir(upload_folder)
             if os.path.isfile(os.path.join(upload_folder, f))]
    if not files: 
        return None
    return max(files, key=os.path.getctime)

def compare_data(request):
    latest = get_latest_uploaded_file()
    if not latest:
        return HttpResponse("No uploaded file found.")

    ext = os.path.splitext(latest)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(latest)
    else:
        df = pd.read_excel(latest, engine='openpyxl')

    df = df.applymap(lambda x: str(x).strip())

    scanned_file = os.path.join(settings.MEDIA_ROOT, 'scanned_awbs.txt')
    if not os.path.exists(scanned_file):
        return HttpResponse("No scanned AWB data found.")

    with open(scanned_file, 'r') as f:
        scanned_set = {line.strip() for line in f if line.strip()}

    if 'Tracking Link' in df.columns:
        df['__awb__'] = df['Tracking Link'].apply(extract_awb_from_url)
    elif 'AWB Number' in df.columns:
        df['__awb__'] = df['AWB Number'].astype(str).str.strip()
    else:
        return HttpResponse("AWB column not found.")

    df['Matched'] = df['__awb__'].isin(scanned_set)

    matched = df[df['Matched']].drop(columns=['Matched'])
    unmatched = df[~df['Matched']].drop(columns=['Matched'])

    # save into media folder
    matched_path = os.path.join(settings.MEDIA_ROOT, 'matched.xlsx')
    unmatched_path = os.path.join(settings.MEDIA_ROOT, 'unmatched.xlsx')
    matched.to_excel(matched_path, index=False)
    unmatched.to_excel(unmatched_path, index=False)

    return render(request, 'result.html', {
        'matched_count': len(matched),
        'unmatched_count': len(unmatched),
        'matched_path': matched_path,
        'unmatched_path': unmatched_path,
    })

def download_matched(request):
    path = os.path.join(settings.MEDIA_ROOT, 'matched.xlsx')
    with open(path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=matched.xlsx'
        return response

def download_unmatched(request):
    path = os.path.join(settings.MEDIA_ROOT, 'unmatched.xlsx')
    with open(path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=unmatched.xlsx'
        return response
