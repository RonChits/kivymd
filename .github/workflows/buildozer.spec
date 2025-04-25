[app]

# Application title
title = My First

# Package name (reverse domain format)
package.name = mykivymdapp

# Package domain (reverse domain format)
package.domain = org.user

# Source directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,jpeg,kv,ttf,json

# Application version
version = 0.1

# Application requirements
requirements = 
    python3==3.8,
    kivy==2.1.0,
    kivymd==0.104.2,
    openssl,
    sqlite3,
    pillow

# Android specific configurations
android.arch = arm64-v8a
android.ndk_path = 
android.sdk_path = 
android.ndk = 23b
android.sdk = 33
android.minapi = 21
android.api = 33
android.gradle_dependencies = 'com.android.tools.build:gradle:7.2.2'
android.allow_backup = True
android.adaptive_icon_foreground = 
android.adaptive_icon_background = 

# Orientation (portrait|landscape|all)
orientation = portrait

# Log level (2=debug, 1=info, 0=warning)
log_level = 1

# Build behavior
[buildozer]
# Configure buildozer behavior
log_level = 1
warn_on_root = 1
android.accept_sdk_license = True

# Optimizations for smaller APK size
android.no_precompile_assets = 1
android.private_storage = False
android.enable_androidx = True

# Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Presplash
presplash.filename = %(source.dir)s//logo.png
icon.filename = %(source.dir)s/logo.png
