[app]

title = Museum Guided Tour System
package.name = museumtour
package.domain = org.rb1b.group10

source.dir = .
source.include_exts = py,png,jpg,jpeg,wav,mp3,mp4,db,json,ttf,kv,txt
source.include_patterns = assets/*,assets/**/*
# Keep the APK focused on runtime files only — dev tooling and any
# previously-generated local databases/caches never need to ship.
source.exclude_dirs = tests,.pytest_cache,__pycache__,.git,.github,venv,.venv
source.exclude_patterns = *.pyc,*.pyo,museum_tours.db

version = 1.0

# Kept deliberately minimal: opencv-python and ffpyplayer are listed as
# OPTIONAL in requirements.txt precisely because they need heavy native
# compilation that is slow and failure-prone to cross-compile for
# Android. The app already falls back gracefully without them (see
# services/camera_service.py and MEDIA_GUIDE.md), so they are left out
# of the Android build to keep it fast and reliable. Add them back here
# later only if you specifically need real device-camera capture or
# real .mp4 playback on Android, and are prepared for a much longer,
# less reliable build.
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.0,sqlalchemy,pillow

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/assets/images/heart_of_ocean_necklace.jpg

# No special device permissions are needed: the app never accesses a
# real camera or GPS on Android in this build (see the requirements
# note above), and all storage is inside the app's own private data
# directory, which needs no permission on modern Android.
android.permissions =

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.ndk = 25b

[buildozer]

log_level = 2
warn_on_root = 1
