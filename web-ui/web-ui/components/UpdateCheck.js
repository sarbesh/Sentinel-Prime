import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator, Modal } from 'react-native';
import UpdateService, { APP_VERSION, PLATFORM } from '../services/update';

const UpdateCheck = ({ visible, onClose }) => {
  const [checking, setChecking] = useState(false);
  const [updateInfo, setUpdateInfo] = useState(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (visible) {
      checkForUpdates();
    }
  }, [visible]);

  const checkForUpdates = async () => {
    setChecking(true);
    try {
      const result = await UpdateService.checkRemoteVersion();
      setUpdateInfo(result);
    } catch (error) {
      console.error('Update check error:', error);
    } finally {
      setChecking(false);
    }
  };

  const downloadUpdate = async () => {
    setDownloading(true);
    try {
      const result = await UpdateService.fetchAndInstallUpdate();
      if (result.success) {
        Alert.alert('Update Ready', 'The update has been downloaded and will be applied on next restart.');
      } else {
        Alert.alert('Update Failed', result.message || 'Failed to download update.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to download update.');
    } finally {
      setDownloading(false);
    }
  };

  const handleUpdate = () => {
    if (updateInfo?.update) {
      Alert.alert(
        'Update Available',
        `A new version (${updateInfo.update.version}) is available.\n\n${updateInfo.update.release_notes || ''}\n\nWould you like to download and install it?`,
        [
          { text: 'Later', style: 'cancel' },
          { text: 'Update Now', onPress: downloadUpdate },
        ]
      );
    }
  };

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.overlay}>
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>Check for Updates</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeText}>×</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.content}>
            <Text style={styles.versionText}>Current Version: {APP_VERSION}</Text>
            <Text style={styles.platformText}>Platform: {PLATFORM}</Text>

            {checking && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#1a73e8" />
                <Text style={styles.loadingText}>Checking for updates...</Text>
              </View>
            )}

            {!checking && updateInfo && (
              <View style={styles.resultContainer}>
                {updateInfo.update_available ? (
                  <>
                    <View style={styles.updateAvailable}>
                      <Text style={styles.updateIcon}>🔄</Text>
                      <Text style={styles.updateTitle}>Update Available!</Text>
                      <Text style={styles.newVersion}>Version {updateInfo.update.version}</Text>
                      {updateInfo.update.release_notes && (
                        <Text style={styles.releaseNotes}>{updateInfo.update.release_notes}</Text>
                      )}
                    </View>
                    <TouchableOpacity
                      style={styles.updateButton}
                      onPress={handleUpdate}
                      disabled={downloading}
                    >
                      {downloading ? (
                        <ActivityIndicator size="small" color="#fff" />
                      ) : (
                        <Text style={styles.updateButtonText}>Download & Install</Text>
                      )}
                    </TouchableOpacity>
                  </>
                ) : (
                  <View style={styles.upToDate}>
                    <Text style={styles.checkIcon}>✓</Text>
                    <Text style={styles.upToDateText}>You're up to date!</Text>
                    <Text style={styles.latestVersionText}>
                      Version {updateInfo.current_version} is the latest version.
                    </Text>
                  </View>
                )}
              </View>
            )}

            {!checking && !updateInfo && (
              <TouchableOpacity style={styles.retryButton} onPress={checkForUpdates}>
                <Text style={styles.retryButtonText}>Check Again</Text>
              </TouchableOpacity>
            )}
          </View>

          <TouchableOpacity style={styles.closeModalButton} onPress={onClose}>
            <Text style={styles.closeModalButtonText}>Close</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  container: {
    backgroundColor: '#fff',
    borderRadius: 16,
    width: '90%',
    maxWidth: 400,
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    padding: 5,
  },
  closeText: {
    fontSize: 28,
    color: '#999',
    lineHeight: 28,
  },
  content: {
    alignItems: 'center',
  },
  versionText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  platformText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 20,
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 30,
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
  },
  resultContainer: {
    width: '100%',
    alignItems: 'center',
  },
  updateAvailable: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#e3f2fd',
    borderRadius: 12,
    width: '100%',
    marginBottom: 20,
  },
  updateIcon: {
    fontSize: 40,
    marginBottom: 10,
  },
  updateTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a73e8',
    marginBottom: 5,
  },
  newVersion: {
    fontSize: 14,
    color: '#1a73e8',
    marginBottom: 10,
  },
  releaseNotes: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  updateButton: {
    backgroundColor: '#1a73e8',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 20,
    width: '100%',
    alignItems: 'center',
  },
  updateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  upToDate: {
    alignItems: 'center',
    padding: 20,
  },
  checkIcon: {
    fontSize: 40,
    color: '#4caf50',
    marginBottom: 10,
  },
  upToDateText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4caf50',
    marginBottom: 5,
  },
  latestVersionText: {
    fontSize: 12,
    color: '#666',
  },
  retryButton: {
    marginTop: 10,
    padding: 10,
  },
  retryButtonText: {
    color: '#1a73e8',
    fontSize: 14,
  },
  closeModalButton: {
    marginTop: 20,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  closeModalButtonText: {
    color: '#666',
    fontSize: 16,
    textAlign: 'center',
  },
});

export default UpdateCheck;
