# 🖥️ LAN Dashboard

A locally-hosted web control panel built with **Django** that lets any device on the same Wi-Fi or hotspot network securely monitor and control a PC — entirely without an internet connection.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Accessing from Other Devices](#accessing-from-other-devices)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Security Model](#security-model)
- [Use Cases](#use-cases)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**LAN Dashboard** is a self-hosted, mobile-first web application that turns any PC into a local control hub.  Once the Django server is running, any smartphone, tablet, or laptop connected to the same Wi-Fi or hotspot can open a browser, log in, and interact with the host machine — no cloud, no internet, no external services required.

```
Phone / Tablet / Laptop  ──── Wi-Fi / Hotspot ────  PC (Django Server)
        Browser                                        Port 8000
```

---

## Features

### 🔐 Authentication & Access Control
- Secure local login / logout with Django's built-in session management
- **Admin** and **User** role separation via Django groups
- All pages require authentication; restricted pages require admin role
- CSRF protection enabled on all forms

### 📊 Live System Dashboard
- Displays real-time **PC hostname**, **LAN IP address**, **server uptime**, and **current date/time**
- Scans the local ARP table to list **connected LAN devices** (IP + MAC address)

### ⚙️ Remote System Control *(Admin only)*
- **Shutdown**, **Restart**, and **Lock Screen** the host machine with a single button
- **Launch programs** remotely from a curated list (Notepad, Calculator, Chrome, PowerShell, etc.) or type a custom executable name

### 📁 Full File Manager *(Admin only)*
- Browse the **entire file system** of the host PC (all drives on Windows, root on Linux)
- **Upload** files from any connected device to the PC
- **Download** any file from the PC to the connected device
- **Delete** files directly from the browser
- **Preview** text files, images, audio, and video inline in the browser

### 📋 Activity Logs *(Admin only)*
- Tracks every user action: logins, file uploads, downloads, deletions, and previews
- Records **username**, **action type**, **file path**, **IP address**, and **timestamp**
- Searchable log table (filter by user, action, path, or IP)

### 🖱️ Phone Mouse *(Admin only)*
- Use a phone's touchpad interface to **control the host PC's mouse cursor in real time**
- Powered by **WebSocket** (Django Channels) for low-latency communication
- Supports **move**, **left click**, **right click**, **press**, and **release** gestures

### 📱 Mobile-First UI
- Responsive layout designed primarily for smartphones and touch screens
- Touch-friendly buttons and controls throughout

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Client Devices (LAN)                 │
│        Phone  /  Tablet  /  Laptop  /  Desktop           │
│                     Web Browser                          │
└──────────────────────┬───────────────────────────────────┘
                       │  HTTP / WebSocket (LAN only)
                       │  e.g. http://192.168.x.x:8000
┌──────────────────────▼───────────────────────────────────┐
│                     Host PC — Django                     │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Django     │  │  Django      │  │  Django        │  │
│  │  Views      │  │  Channels    │  │  Auth +        │  │
│  │  (HTTP)     │  │  (WebSocket) │  │  Sessions      │  │
│  └──────┬──────┘  └──────┬───────┘  └────────────────┘  │
│         │                │                               │
│  ┌──────▼────────────────▼──────────────────────────┐   │
│  │              SQLite Database                      │   │
│  │         (users, groups, activity logs)            │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
│  ┌───────────────────┐   ┌───────────────────────────┐  │
│  │  OS / File System │   │  PyAutoGUI (mouse control)│  │
│  │  (Windows/Linux)  │   │                           │  │
│  └───────────────────┘   └───────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**No API calls outside the network. Everything stays local.**

---

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.10 or newer |
| pip | Latest |
| Django | 5.x |
| Django Channels | 4.x |
| Daphne (ASGI server) | 4.x |
| PyAutoGUI | Latest |

> **Note:** The Phone Mouse feature (`pyautogui`) requires a display. On headless Linux servers you may need to configure a virtual display (e.g., `Xvfb`).

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Marvin-Codex/LAN-Dashboard.git
cd LAN-Dashboard
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django channels daphne pyautogui
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username and password. This account will have full admin access in the dashboard.

### 6. Collect static files

```bash
python manage.py collectstatic --noinput
```

---

## Configuration

All configuration lives in `lan_dashboard/settings.py`.

| Setting | Default | Notes |
|---|---|---|
| `ALLOWED_HOSTS` | `['*']` | Accepts all hosts on the LAN. Restrict to specific IPs for tighter security. |
| `DEBUG` | `True` | Set to `False` for production-like deployments. |
| `TIME_ZONE` | `'UTC'` | Change to your local timezone (e.g. `'Africa/Kampala'`). |
| `DATABASES` | SQLite | No external database needed. |
| `LOGIN_URL` | `'/login/'` | Redirect for unauthenticated users. |
| `LOGIN_REDIRECT_URL` | `'/'` | Redirect after successful login. |

> ⚠️ **Important:** Replace the `SECRET_KEY` in `settings.py` with a strong, randomly generated key before sharing or deploying the project.

---

## Running the Server

### Using Daphne (recommended — supports WebSocket for Phone Mouse)

```bash
daphne -b 0.0.0.0 -p 8000 lan_dashboard.asgi:application
```

### Using Django's development server (HTTP only — Phone Mouse will not work)

```bash
python manage.py runserver 0.0.0.0:8000
```

`0.0.0.0` binds the server to all network interfaces so it is reachable from other devices on the LAN.

---

## Accessing from Other Devices

1. Find the **LAN IP address** of the host PC:
   - **Windows:** Run `ipconfig` in a command prompt and look for the IPv4 address (e.g., `192.168.1.5`).
   - **Linux/macOS:** Run `ip addr` or `hostname -I`.

2. On any device connected to the **same Wi-Fi or hotspot**, open a browser and navigate to:

   ```
   http://<HOST-PC-IP>:8000
   ```

   Example: `http://192.168.1.5:8000`

3. Log in with the superuser credentials created during installation.

---

## Usage

### URL Reference

| URL | Description | Access |
|---|---|---|
| `/` | Main dashboard | All logged-in users |
| `/login/` | Login page | Public |
| `/logout/` | Logout | All logged-in users |
| `/files/` | File manager — browse, upload, download, delete, preview | Admin only |
| `/download/<filename>/` | Direct file download (uses `?path=` query param) | Admin only |
| `/preview/<filename>/` | Inline file preview (uses `?path=` query param) | Admin only |
| `/activity-logs/` | User activity log viewer with search | Admin only |
| `/phone-mouse/` | WebSocket-powered touchpad mouse controller | Admin only |

### Creating Additional Users

Use the Django admin panel at `/admin/` to create additional user accounts and assign them to the `admin` group to grant admin privileges.

---

## Project Structure

```
LAN-Dashboard/
├── dashboard/                  # Main Django application
│   ├── migrations/             # Database migrations
│   ├── static/dashboard/       # Custom CSS (style.css)
│   ├── templates/dashboard/    # HTML templates
│   │   ├── base.html           # Base layout
│   │   ├── login.html          # Login page
│   │   ├── dashboard.html      # Main dashboard
│   │   ├── file_manager.html   # File manager
│   │   ├── activity_logs.html  # Activity log viewer
│   │   └── phone_mouse.html    # Phone mouse touchpad
│   ├── admin.py                # Django admin registrations
│   ├── apps.py                 # App configuration
│   ├── consumers.py            # WebSocket consumer (Phone Mouse)
│   ├── models.py               # UserActivityLog model
│   ├── routing.py              # WebSocket URL routing
│   ├── urls.py                 # HTTP URL routing
│   └── views.py                # All view logic
├── lan_dashboard/              # Django project configuration
│   ├── asgi.py                 # ASGI entry point (HTTP + WebSocket)
│   ├── settings.py             # Project settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI entry point
├── staticfiles/                # Collected static files (after collectstatic)
├── db.sqlite3                  # SQLite database (created after migrate)
├── manage.py                   # Django management utility
└── LICENSE
```

---

## Security Model

| Layer | Implementation |
|---|---|
| **Network scope** | Server binds to LAN interface only; not exposed to the internet |
| **Authentication** | Django session-based login required for every page |
| **Authorization** | Admin-only features gated by group membership check on every request |
| **CSRF protection** | Django's `CsrfViewMiddleware` enabled on all POST forms |
| **File access control** | File manager prevents path traversal; operations are validated to stay within the resolved path |
| **WebSocket security** | Phone Mouse WebSocket connection validates session and admin role on connect; closes immediately if unauthorized |

> **Reminder:** This application is designed for trusted local networks. Do not expose port 8000 to the public internet without additional hardening (firewall rules, a reverse proxy with TLS, etc.).

---

## Use Cases

- **Home PC remote control** — Control your desktop from your phone while sitting across the room
- **Offline classroom system** — Teacher's PC as a server; students access shared resources on tablets
- **Cyber café management** — Monitor and control multiple machines from a central admin device
- **Local attendance tracking** — Log-in based activity tracking without any cloud dependency
- **Company intranet kiosk** — Internal dashboard for an office without public internet
- **Embedded/IoT control panel** — Manage a Raspberry Pi or local server from any browser on the network

---

## Contributing

Contributions are welcome! To get started:

1. Fork this repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request against the `main` branch

Please keep code style consistent with the existing codebase and test changes on at least one LAN-connected device before submitting.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for full details.

© 2026 Sserunjoji Marvin
