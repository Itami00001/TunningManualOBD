[app]

# (str) Title of your application
title = VIN Reader

# (str) Package name
package.name = vinreader

# (str) Package domain (needed for android/ios packaging)
package.domain = org.vinreader

# (str) Source files where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude
#source.exclude_exts = spec

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,kivymd,python-obd,nhtsa-vin-decoder,pyjnius,plyer,requests,openssl

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of LANDSCAPE, PORTRAIT or all)
orientation = portrait

# (list) List of allowed to seek permission on android
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_CONNECT,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,BLUETOOTH_PRIVILEGED

# (int) Target Android API, should be as high as possible.
android.api = 30

# (int) Minimum Android API, should be as low as possible
android.minapi = 21

# (int) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# This can be necessary for CI builds
android.accept_sdk_license = True

# (str) Android entry point, default is 'org.kivy.android.PythonActivity'
# This can be used to customize the launch arguments or provide a
# custom entry point
#android.entrypoint = org.kivy.android.PythonActivity

# Android's logcat can be monitored and logged at build time
#android.logcat_filters = *:S python:D

# (str) Public library to add to the APK
android.archs = arm64-v8a,armeabi-v7a

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Android additional libraries
# android.add_libs = python3

# (bool) Copy instead of symlinking libraries
android.copy_libs = 1

# (str) Android SDK path (set via environment in CI)
# android.sdk_path = /home/start/android-sdk

# (bool) Whether you want to add a custom bootstrap.py
#android.bootstrap_py = 

# (str) Python for android branch to use
#p4a.branch = master

# (str) Python for android repository to use
#p4a.repo = 

# (str) Fork of python-for-android to use
#p4a.fork = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
