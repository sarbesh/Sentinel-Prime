import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking, Platform } from 'react-native';
import ApiService from '../services/api';

const STATIC_DOWNLOADS = [
  {
    id: 'web',
    name: 'Web App',
    description: 'Run in any browser - Progressive Web App (PWA)',
    icon: '🌐',
    url: '/',
    platform: 'web',
  },
  {
    id: 'android',
    name: 'Android APK',
    description: 'Install on Android devices - No app store required',
    icon: '📱',
    url: 'http://localhost:8000/downloads/sentinel-prime-android.apk',
    platform: 'android',
  },
  {
    id: 'ios',
    name: 'iOS App',
    description: 'Install on iPhone/iPad - Requires iOS 14+',
    icon: '🍎',
    url: 'http://localhost:8000/downloads/sentinel-prime-ios.ipa',
    platform: 'ios',
  },
  {
    id: 'windows',
    name: 'Windows',
    description: 'Windows 10/11 x64 installer',
    icon: '🪟',
    url: 'http://localhost:8000/downloads/Sentinel-Prime-Setup.exe',
    platform: 'windows',
  },
  {
    id: 'linux',
    name: 'Linux',
    description: 'Linux AppImage - Works on most distributions',
    icon: '🐧',
    url: 'http://localhost:8000/downloads/sentinel-prime-linux.AppImage',
    platform: 'linux',
  },
];

const DownloadsScreen = () => {
  const [currentPlatform, setCurrentPlatform] = useState('web');
  const [availableDownloads, setAvailableDownloads] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const detectPlatform = () => {
      const ua = navigator.userAgent.toLowerCase();
      if (ua.includes('android')) {
        setCurrentPlatform('android');
      } else if (ua.includes('iphone') || ua.includes('ipad')) {
        setCurrentPlatform('ios');
      } else if (ua.includes('win')) {
        setCurrentPlatform('windows');
      } else if (ua.includes('linux')) {
        setCurrentPlatform('linux');
      } else {
        setCurrentPlatform('web');
      }
    };
    detectPlatform();
    fetchAvailableDownloads();
  }, []);

  const fetchAvailableDownloads = async () => {
    try {
      const downloads = await ApiService.request('/downloads');
      const available = {};
      downloads.forEach(d => {
        available[d.id] = d.size > 0;
      });
      setAvailableDownloads(available);
    } catch (error) {
      console.log('Could not fetch downloads:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (url) => {
    if (url === '/') {
      return;
    }
    Linking.openURL(url);
  };

  const getRecommended = () => {
    const recommended = STATIC_DOWNLOADS.find(d => d.platform === currentPlatform && (availableDownloads[d.id] || d.platform === 'web'));
    return recommended || STATIC_DOWNLOADS.find(d => availableDownloads[d.id] || d.platform === 'web') || STATIC_DOWNLOADS[0];
  };

  const isAvailable = (platform) => {
    return availableDownloads[platform] || platform === 'web';
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Download Sentinel Prime</Text>
      <Text style={styles.subtitle}>Get the app on your preferred platform</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recommended for You</Text>
        <TouchableOpacity
          style={styles.recommendedCard}
          onPress={() => handleDownload(getRecommended().url)}
        >
          <Text style={styles.recommendedIcon}>{getRecommended().icon}</Text>
          <View style={styles.recommendedInfo}>
            <Text style={styles.recommendedName}>{getRecommended().name}</Text>
            <Text style={styles.recommendedDesc}>{getRecommended().description}</Text>
          </View>
          <Text style={styles.downloadButton}>Download</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>All Platforms</Text>
        {STATIC_DOWNLOADS.map((app) => (
          <TouchableOpacity
            key={app.id}
            style={[
              styles.appCard,
              app.platform === currentPlatform && styles.currentPlatformCard,
              !isAvailable(app.platform) && styles.unavailableCard
            ]}
            onPress={() => isAvailable(app.platform) && handleDownload(app.url)}
            disabled={!isAvailable(app.platform)}
          >
            <Text style={styles.appIcon}>{app.icon}</Text>
            <View style={styles.appInfo}>
              <Text style={[styles.appName, !isAvailable(app.platform) && styles.unavailableText]}>
                {app.name}
              </Text>
              <Text style={styles.appDesc}>
                {isAvailable(app.platform) ? app.description : 'Not yet built - Run build script to create'}
              </Text>
            </View>
            {app.platform === currentPlatform && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>Current</Text>
              </View>
            )}
            {!isAvailable(app.platform) && app.platform !== 'web' && (
              <View style={styles.unavailableBadge}>
                <Text style={styles.unavailableBadgeText}>N/A</Text>
              </View>
            )}
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Start</Text>
        <View style={styles.instructionCard}>
          <Text style={styles.instructionTitle}>1. Backend Required</Text>
          <Text style={styles.instructionText}>
            Make sure the Sentinel Prime backend is running on port 8000
          </Text>
        </View>
        <View style={styles.instructionCard}>
          <Text style={styles.instructionTitle}>2. First Time?</Text>
          <Text style={styles.instructionText}>
            Create an account using the app to start monitoring your network
          </Text>
        </View>
        <View style={styles.instructionCard}>
          <Text style={styles.instructionTitle}>3. Network Access</Text>
          <Text style={styles.instructionText}>
            For mobile apps, ensure your device can reach the backend server
          </Text>
        </View>
      </View>

      <View style={styles.versionInfo}>
        <Text style={styles.versionText}>Version 1.0.0</Text>
        <Text style={styles.copyrightText}>Sentinel Prime - Home Network Security</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 50,
    marginHorizontal: 20,
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginHorizontal: 20,
    marginBottom: 20,
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  recommendedCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e3f2fd',
    borderRadius: 12,
    padding: 15,
    borderWidth: 2,
    borderColor: '#1a73e8',
  },
  recommendedIcon: {
    fontSize: 40,
    marginRight: 15,
  },
  recommendedInfo: {
    flex: 1,
  },
  recommendedName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a73e8',
  },
  recommendedDesc: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  downloadButton: {
    backgroundColor: '#1a73e8',
    color: '#fff',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    fontWeight: 'bold',
    fontSize: 14,
  },
  appCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f9f9f9',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
  },
  currentPlatformCard: {
    backgroundColor: '#e8f5e9',
    borderWidth: 1,
    borderColor: '#4caf50',
  },
  appIcon: {
    fontSize: 32,
    marginRight: 15,
  },
  appInfo: {
    flex: 1,
  },
  appName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  appDesc: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  unavailableCard: {
    opacity: 0.6,
    backgroundColor: '#f0f0f0',
  },
  unavailableText: {
    color: '#999',
  },
  unavailableBadge: {
    backgroundColor: '#ccc',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  unavailableBadgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  badge: {
    backgroundColor: '#4caf50',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  instructionCard: {
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
  },
  instructionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  instructionText: {
    fontSize: 12,
    color: '#666',
  },
  versionInfo: {
    alignItems: 'center',
    padding: 20,
    marginBottom: 40,
  },
  versionText: {
    fontSize: 12,
    color: '#999',
  },
  copyrightText: {
    fontSize: 11,
    color: '#ccc',
    marginTop: 4,
  },
});

export default DownloadsScreen;
