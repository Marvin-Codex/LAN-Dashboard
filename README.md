🧩 Django LAN Dashboard — Description

A Django LAN Dashboard is a locally hosted web control panel that runs on a PC and is accessed by other devices (phones, tablets, laptops) connected to the same hotspot or Wi-Fi network, without using the internet.

The system works entirely on a local area network (LAN).

🔧 How it works

PC runs Django server (0.0.0.0)

Phone connects via hotspot

Phone browser accesses:

http://PC-IP:8000


Django serves pages in real time over LAN

No cloud.
No internet.
No external services.

🎯 Purpose

The LAN dashboard allows users to monitor, control, or manage a system from any device on the same network.

It behaves like:

Router admin panel

School intranet system

Office internal dashboard

🧠 Core features
1. Authentication

Local login system

Admin / user roles

Session-based access

2. Live system information

PC name

IP address

Connected devices

Server uptime

Date & time

3. Control actions (optional)

Shutdown PC

Restart PC

Lock screen

Start programs

Manage background tasks

(Executed securely on server side)

4. File access (LAN)

Upload files from phone to PC

Download files from PC

Share folders locally

5. Activity logs

Login history

Action logs

Time tracking

6. Mobile-first interface

Designed mainly for phones

Touch-friendly dashboard

Responsive layout

🏗 Architecture
Phone Browser
      ↓
HTTP Requests (LAN)
      ↓
Django Views
      ↓
System Controller (Python)
      ↓
Windows OS


No APIs outside the network.

🧪 Example use cases

PC remote controller

Offline school system

Cyber café management

Local attendance system

Offline company intranet

Testing backend systems without internet

🔐 Security model

Accessible only inside LAN

Login required

Optional IP whitelisting

CSRF + session security

No public exposure

🧠 Why this is important (engineering-wise)

This project teaches:

Client–server architecture

Network communication

LAN routing

Port binding

Backend system control

Real-world Django deployment logic

This is real software engineering, not CRUD only.

📌 Summary (short)

A Django LAN Dashboard is a locally hosted web-based control system that allows devices on the same network to securely access and manage a computer or internal system without internet connectivity.

If you want next, I can give you:

✅ project folder structure

✅ feature list for coursework

✅ database models

✅ dashboard UI layout

✅ step-by-step build plan

Just say which one.











Sprint 1: Project Setup & Authentication

Initialize Django project/app.
Set up local static files for custom CSS/JS.
Implement local login system (admin/user roles).
Create basic dashboard page (mobile-first, custom styling).
Sprint 2: System Info & Control Actions

Display PC name, IP, connected devices, uptime, date/time.
Add secure server-side actions: shutdown, restart, lock, start programs.
Sprint 3: File Access & Activity Logs

Enable file upload/download/share over LAN.
Implement login history, action logs, time tracking.
Sprint 4: UI/UX & Security

Refine dashboard for mobile/touch.
Add IP whitelisting, CSRF/session security.
Polish custom styling, ensure no CDN/external resources.
Sprint 5: Testing & Deployment

Test on multiple devices in LAN.
Document usage and deployment steps.
Finalize for local deployment (no internet required).
