from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden, FileResponse, HttpResponse, HttpResponseNotFound
from django.conf import settings
from mimetypes import guess_type
import socket, os, platform
from urllib.parse import unquote, quote
from .models import UserActivityLog
from django.db import models

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'dashboard/login.html', {'form': request.POST, 'errors': True})
    return render(request, 'dashboard/login.html')

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Helper: Scan LAN for connected devices (simple ARP table parse)
def get_connected_devices():
    devices = []
    if os.name == 'nt':
        output = os.popen('arp -a').read()
        for line in output.splitlines():
            if '-' in line:
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({'ip': parts[0], 'mac': parts[1]})
    else:
        output = os.popen('arp -a').read()
        for line in output.splitlines():
            if 'at' in line:
                parts = line.split()
                devices.append({'ip': parts[1], 'mac': parts[3]})
    return devices

# Helper: Check if user is admin
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

def log_user_activity(request, action, path=None):
    ip = request.META.get('REMOTE_ADDR')
    if request.user.is_authenticated:
        UserActivityLog.objects.create(user=request.user, action=action, path=path, ip_address=ip)

# Dashboard view
@login_required
def dashboard_view(request):
    pc_name = socket.gethostname()
    ip_address = socket.gethostbyname(pc_name)
    if os.name == 'nt':
        stats = os.popen('net stats workstation').read()
        if 'Statistics since' in stats:
            uptime = stats.split('Statistics since')[1].split('\n')[0].strip()
        else:
            uptime = 'Unavailable'
    else:
        uptime = os.popen('uptime -p').read().strip()
    date_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    devices = get_connected_devices()
    action_result = None
    if request.method == 'POST' and is_admin(request.user):
        action = request.POST.get('action')
        if action == 'shutdown':
            os.system('shutdown /s /t 1' if os.name == 'nt' else 'shutdown now')
            action_result = 'Shutdown command sent.'
        elif action == 'restart':
            os.system('shutdown /r /t 1' if os.name == 'nt' else 'reboot')
            action_result = 'Restart command sent.'
        elif action == 'lock':
            os.system('rundll32.exe user32.dll,LockWorkStation' if os.name == 'nt' else 'xdg-screensaver lock')
            action_result = 'Lock command sent.'
        elif action == 'start_program':
            prog = request.POST.get('program', 'notepad' if os.name == 'nt' else 'gedit')
            if prog == 'custom':
                custom_prog = request.POST.get('custom_program', '').strip()
                if custom_prog:
                    prog = custom_prog
            os.system(prog)
            action_result = f'Started program: {prog}'
    elif request.method == 'POST':
        return HttpResponseForbidden('Admin only action.')
    if request.user.is_authenticated:
        log_user_activity(request, 'dashboard_login')
    return render(request, 'dashboard/dashboard.html', {
        'user': request.user,
        'pc_name': pc_name,
        'ip_address': ip_address,
        'uptime': uptime,
        'date_time': date_time,
        'devices': devices,
        'is_admin': is_admin(request.user),
        'action_result': action_result,
    })

# File manager view
@login_required
def file_manager_view(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Admins only.')
    # Detect platform and set up root/partitions
    is_windows = platform.system() == 'Windows'
    base_path = os.path.abspath(os.sep)
    req_path = request.GET.get('path')
    if not req_path:
        # No path provided: show all drives (Windows) or root (Unix)
        if is_windows:
            import string
            from ctypes import windll
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:/")
                bitmask >>= 1
            return render(request, 'dashboard/file_manager.html', {
                'folders': drives,
                'files': [],
                'current_path': '',
                'parent_path': None,
                'error': None,
                'file_previews': {},
                'is_drive_root': True,
            })
        else:
            req_path = base_path
    current_path = os.path.abspath(unquote(req_path))
    # Prevent escaping root on Unix, allow any drive on Windows
    if not is_windows and not current_path.startswith(base_path):
        current_path = base_path
    parent_path = os.path.dirname(current_path) if current_path != base_path else None
    error = None
    # Handle file upload (uploads to current_path if writable)
    if request.method == 'POST':
        if request.FILES.get('file'):
            f = request.FILES['file']
            try:
                with open(os.path.join(current_path, f.name), 'wb+') as dest:
                    for chunk in f.chunks():
                        dest.write(chunk)
                log_user_activity(request, 'upload', os.path.join(current_path, f.name))
            except Exception as e:
                error = f"Upload failed: {e}"
        elif request.POST.get('delete_file'):
            file_to_delete = request.POST.get('delete_file')
            file_path = os.path.join(current_path, file_to_delete)
            # Only allow delete if file is inside current_path and not a directory
            if os.path.exists(file_path) and os.path.isfile(file_path) and file_path.startswith(current_path):
                try:
                    os.remove(file_path)
                    log_user_activity(request, 'delete', file_path)
                except Exception as e:
                    error = f"Delete failed: {e}"
    # List folders and files
    try:
        entries = os.listdir(current_path)
        folders = sorted([e for e in entries if os.path.isdir(os.path.join(current_path, e))])
        files = sorted([e for e in entries if os.path.isfile(os.path.join(current_path, e))])
    except Exception as e:
        folders, files = [], []
        error = f"Cannot access directory: {e}"
    # Generate preview URLs for each file
    file_previews = {}
    for file in files:
        file_path = os.path.join(current_path, file)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_previews[file] = {
                'url': f"/file_preview/?path={quote(current_path)}&file={quote(file)}",
                'mime': guess_type(file_path)[0] or 'application/octet-stream',
            }
    return render(request, 'dashboard/file_manager.html', {
        'folders': folders,
        'files': files,
        'current_path': current_path,
        'parent_path': parent_path,
        'error': error,
        'file_previews': file_previews,
        'is_drive_root': False,
    })

@login_required
def download_file_view(request, filename):
    if not is_admin(request.user):
        return HttpResponseForbidden('Admins only.')
    base_path = os.path.abspath(os.sep)
    req_path = request.GET.get('path', base_path)
    current_path = os.path.abspath(unquote(req_path))
    if platform.system() == 'Windows' and len(current_path) == 2 and current_path[1] == ':':
        current_path += '\\'
    if not platform.system() == 'Windows' and not current_path.startswith(base_path):
        current_path = base_path
    file_path = os.path.join(current_path, filename)
    file_path = os.path.normpath(file_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        log_user_activity(request, 'download', file_path)
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    return HttpResponseForbidden('File not found or forbidden.')

@login_required
def file_preview_view(request, filename):
    if not is_admin(request.user):
        return HttpResponseForbidden('Admins only.')
    base_path = os.path.abspath(os.sep)
    req_path = request.GET.get('path', base_path)
    current_path = os.path.abspath(unquote(req_path))
    # On Windows, allow drive root and handle backslashes
    if platform.system() == 'Windows' and len(current_path) == 2 and current_path[1] == ':':
        current_path += '\\'
    if not platform.system() == 'Windows' and not current_path.startswith(base_path):
        current_path = base_path
    file_path = os.path.join(current_path, filename)
    # Normalize file_path for Windows
    file_path = os.path.normpath(file_path)
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        return HttpResponseNotFound('File not found or forbidden.')
    log_user_activity(request, 'preview', file_path)
    mime, _ = guess_type(file_path)
    if not mime:
        mime = 'application/octet-stream'
    if mime.startswith('text'):
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return HttpResponse(f.read(), content_type=mime)
    elif mime.startswith('image') or mime.startswith('audio') or mime.startswith('video'):
        return FileResponse(open(file_path, 'rb'), content_type=mime)
    else:
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)

@login_required
def activity_logs_view(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Admins only.')
    q = request.GET.get('q', '').strip()
    logs = UserActivityLog.objects.all().order_by('-timestamp')
    if q:
        logs = logs.filter(
            models.Q(user__username__icontains=q) |
            models.Q(action__icontains=q) |
            models.Q(path__icontains=q) |
            models.Q(ip_address__icontains=q)
        )
    logs = logs.select_related('user')[:200]
    return render(request, 'dashboard/activity_logs.html', {'logs': logs})

@login_required
def phone_mouse_view(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Admins only.')
    return render(request, 'dashboard/phone_mouse.html')