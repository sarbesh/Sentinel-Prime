# Sentinel Prime Web UI

A cross-platform web interface for the Sentinel Prime network security monitoring system.

## Features

- Dashboard with statistics
- Device management (view, add test devices)
- Scan management (view scans, trigger new scans)
- Alerts viewing
- Settings management

## Prerequisites

- Node.js (v16 or later)
- npm or yarn
- Running Sentinel Prime backend (accessible at http://localhost:8000)

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser to http://localhost:5173 (or the URL shown in the terminal)

## Building for Production

To build the webapp for production:

```bash
npm run build
```

The built files will be in the `dist` directory.

## Docker

To run the webapp in a Docker container (optional), you can create a Dockerfile:

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Then build and run:

```bash
docker build -t sentinel-prime-webui .
docker run -p 80:80 sentinel-prime-webui
```

## API Endpoints Used

The webapp interacts with the following backend endpoints:

- GET `/devices` - List all devices
- POST `/devices` - Add a new device (test function)
- GET `/scans` - List all scans
- POST `/scans/network` - Trigger a new network scan
- GET `/alerts` - List all alerts
- GET `/settings` - List all settings
- POST `/settings` - Update a setting

Note: The vulnerabilities endpoint is not currently used in the UI but is available at `/scans/vulnerabilities`.

## Customization

To change the API URL, modify the API calls in the components to use a different base URL or environment variable.

## License

MIT