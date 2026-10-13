@echo off
echo === AccionGPS Manager Build ===
echo.

set JAVA_TOOL_OPTIONS=-Xmx4g
set FLUTTER=C:\Users\PC\Desktop\flutter\bin\flutter.bat

cd /d C:\apks2026\acciongps

echo Building APK...
"%FLUTTER%" build apk --release --android-skip-build-dependency-validation
if %ERRORLEVEL% neq 0 (
    echo BUILD FAILED!
    pause
    exit /b 1
)

echo.
echo APK generated at:
echo   C:\apks2026\acciongps\build\app\outputs\flutter-apk\app-release.apk
echo.
pause
