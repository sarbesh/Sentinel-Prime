# Downloads Directory

Place your built application files here to make them available for download from the web UI.

## File Naming Convention

Place your built files with these names:
- `sentinel-prime-android.apk` - Android APK
- `sentinel-prime-ios.ipa` - iOS App
- `Sentinel-Prime-Setup.exe` - Windows Installer
- `sentinel-prime-linux.AppImage` - Linux AppImage

## How to Build

### From the host machine:

```bash
# Build web assets
cd web-ui/web-ui
npx expo export --platform web

# Build Android (requires Android SDK)
cd web-ui/web-ui
npx expo prebuild --platform android
cd android
./gradlew assembleRelease

# Copy to downloads
cp android/app/build/outputs/apk/release/app-release.apk ../../../../downloads/sentinel-prime-android.apk
```

### Using the build script:

```bash
chmod +x web-ui/scripts/build.sh
./web-ui/scripts/build.sh android
```

The built files will be in:
- Android: `web-ui/android/app/build/outputs/apk/release/`

## Accessing Downloads

Once files are placed here and Docker is rebuilt/restarted:
- Web UI: http://localhost:3000
- Downloads tab: Shows download links
- Direct download: http://localhost:3000/downloads/

## Rebuilding the UI Container

After adding files to this directory, rebuild the UI container:

```bash
docker-compose build ui
docker-compose up -d ui
```
