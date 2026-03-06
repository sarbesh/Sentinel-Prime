import * as Updates from 'expo-updates';
import { Platform } from 'react-native';

const APP_VERSION = '1.0.0';

export const PLATFORM = Platform.OS;

class UpdateService {
  async checkForUpdates() {
    try {
      if (__DEV__) {
        console.log('Update check skipped in development mode');
        return { updateAvailable: false, currentVersion: APP_VERSION };
      }

      const update = await Updates.checkForUpdateAsync();
      
      if (update.isAvailable) {
        return {
          updateAvailable: true,
          currentVersion: APP_VERSION,
          version: update.version,
          manifest: update.manifest,
        };
      }
      
      return { updateAvailable: false, currentVersion: APP_VERSION };
    } catch (error) {
      console.log('Error checking for updates:', error);
      return { updateAvailable: false, currentVersion: APP_VERSION, error: error.message };
    }
  }

  async downloadAndApplyUpdate() {
    try {
      if (__DEV__) {
        console.log('Update download skipped in development mode');
        return { success: false, message: 'Updates not available in development' };
      }

      const update = await Updates.checkForUpdateAsync();
      
      if (update.isAvailable) {
        await update.downloadAsync();
        return { success: true, message: 'Update downloaded. Restart to apply.' };
      }
      
      return { success: false, message: 'No update available' };
    } catch (error) {
      console.log('Error downloading update:', error);
      return { success: false, message: error.message };
    }
  }

  async checkRemoteVersion() {
    try {
      const apiUrl = this.getApiBaseUrl();
      const response = await fetch(`${apiUrl}/updates/check?platform=${PLATFORM}&current_version=${APP_VERSION}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.log('Error checking remote version:', error);
      return { update_available: false, current_version: APP_VERSION };
    }
  }

  getApiBaseUrl() {
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      const protocol = window.location.protocol;
      return `${protocol}//${hostname}:8000`;
    }
    return 'http://localhost:8000';
  }

  async fetchAndInstallUpdate() {
    try {
      const update = await Updates.checkForUpdateAsync();
      
      if (update.isAvailable) {
        await update.downloadAsync();
        await Updates.reloadAsync();
        return { success: true };
      }
      
      return { success: false, message: 'No update available' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }
}

export default new UpdateService();
export { APP_VERSION, PLATFORM };
