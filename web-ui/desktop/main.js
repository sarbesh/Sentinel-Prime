const { app, BrowserWindow, ipcMain, shell, dialog } = require('electron');
const path = require('path');
const { autoUpdater } = require('electron-updater');

let mainWindow = null;

const UPDATE_SERVER_URL = 'http://localhost:3000/downloads';

function createWindow() {
  const isDev = !app.isPackaged;
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'Sentinel Prime',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: true,
    },
    show: false,
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    console.log('Sentinel Prime Desktop started');
  });

  if (isDev) {
    mainWindow.loadFile(path.join(__dirname, 'web-build', 'index.html'));
  } else {
    mainWindow.loadFile(path.join(__dirname, 'web-build', 'index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

function setupAutoUpdater() {
  autoUpdater.autoDownload = false;
  autoUpdater.autoInstallOnAppQuit = true;
  
  autoUpdater.on('checking-for-update', () => {
    console.log('Checking for update...');
    if (mainWindow) {
      mainWindow.webContents.send('update-status', { status: 'checking' });
    }
  });

  autoUpdater.on('update-available', (info) => {
    console.log('Update available:', info.version);
    if (mainWindow) {
      mainWindow.webContents.send('update-status', { 
        status: 'available', 
        version: info.version,
        releaseNotes: info.releaseNotes
      });
    }
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `A new version (${info.version}) is available. Would you like to download it?`,
      buttons: ['Download', 'Later']
    }).then(result => {
      if (result.response === 0) {
        autoUpdater.downloadUpdate();
      }
    });
  });

  autoUpdater.on('update-not-available', () => {
    console.log('Update not available');
    if (mainWindow) {
      mainWindow.webContents.send('update-status', { status: 'not-available' });
    }
  });

  autoUpdater.on('download-progress', (progress) => {
    console.log('Download progress:', progress.percent);
    if (mainWindow) {
      mainWindow.webContents.send('update-status', { 
        status: 'downloading', 
        percent: progress.percent 
      });
    }
  });

  autoUpdater.on('update-downloaded', (info) => {
    console.log('Update downloaded:', info.version);
    if (mainWindow) {
      mainWindow.webContents.send('update-status', { 
        status: 'downloaded', 
        version: info.version 
      });
    }
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: 'Update has been downloaded. Restart now to apply the update?',
      buttons: ['Restart', 'Later']
    }).then(result => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  });

  autoUpdater.on('error', (err) => {
    console.error('Auto-updater error:', err);
    if (mainWindow) {
      mainWindow.webContents.send('update-status', { 
        status: 'error', 
        message: err.message 
      });
    }
  });
}

app.whenReady().then(() => {
  createWindow();
  setupAutoUpdater();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-platform', () => {
  return process.platform;
});

ipcMain.handle('check-for-updates', async () => {
  try {
    if (app.isPackaged) {
      await autoUpdater.checkForUpdates();
      return { success: true };
    }
    return { success: false, message: 'Updates only work in production builds' };
  } catch (error) {
    return { success: false, message: error.message };
  }
});

ipcMain.handle('download-update', async () => {
  try {
    await autoUpdater.downloadUpdate();
    return { success: true };
  } catch (error) {
    return { success: false, message: error.message };
  }
});

ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});
