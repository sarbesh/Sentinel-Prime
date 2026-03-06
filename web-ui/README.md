# Sentinel Prime Web & Mobile UI (React Native + Expo)

This UI serves both web and mobile via one codebase, built with Expo (React Native).

## Quickstart

1. Install [NVM](https://github.com/nvm-sh/nvm) and use latest Node LTS:
   ```bash
   # Install NVM
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
   # Restart or reload your shell (see NVM docs)
   nvm install --lts
   nvm use --lts
   # Install Expo CLI
   npm install -g expo-cli
   ```
2. Install dependencies and start development server:
   ```bash
   cd web-ui/web-ui
   npm install
   expo start
   ```
3. The app will run in a browser, and can also be deployed to mobile devices

## Project Structure

```
web-ui/
├── web-ui/
│   ├── App.js                 # Main app with navigation
│   ├── services/
│   │   └── api.js            # Backend API service
│   ├── screens/
│   │   ├── DashboardScreen.js   # Overview with stats
│   │   ├── DevicesScreen.js     # Device management (CRUD)
│   │   ├── AlertsScreen.js      # Security alerts
│   │   └── SettingsScreen.js    # App settings
│   └── package.json
└── README.md
```

## Screens

### Dashboard
- Overview of total devices, online devices, pending alerts, critical alerts
- Recent alerts list
- Device list preview

### Devices
- List all network devices
- Add/Edit/Delete devices
- Filter by type and status

### Alerts
- View all security alerts
- Filter by status (All/Pending/Acknowledged)
- Acknowledge alerts

### Settings
- Toggle notifications, email alerts, dark mode
- Enable/disable honeypot, IPS/IDS
- Network configuration
- Data export options

## API Integration

The app connects to the backend at `http://localhost:8000`. Update `services/api.js` to change the API URL.

## Contributing
- Add screens or features modularly
- Integrate backend API for data
- UI is meant for web and mobile from the same codebase

---

**Note:** The mobile app is included as part of this Expo project; all screens and features should support both platforms.
