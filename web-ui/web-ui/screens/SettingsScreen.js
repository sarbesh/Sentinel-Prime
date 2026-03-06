import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch, Alert } from 'react-native';
import UpdateCheck from '../components/UpdateCheck';
import { APP_VERSION, PLATFORM } from '../services/update';

const SettingsScreen = () => {
  const [settings, setSettings] = useState({
    notifications: true,
    emailAlerts: false,
    darkMode: false,
    autoScan: false,
    honeypotEnabled: false,
    ipsEnabled: false,
  });
  const [showUpdateModal, setShowUpdateModal] = useState(false);

  const toggleSetting = (key) => {
    setSettings({ ...settings, [key]: !settings[key] });
  };

  const renderSettingItem = (title, description, key, isSwitch = true) => (
    <View style={styles.settingItem}>
      <View style={styles.settingInfo}>
        <Text style={styles.settingTitle}>{title}</Text>
        <Text style={styles.settingDescription}>{description}</Text>
      </View>
      {isSwitch && (
        <Switch
          value={settings[key]}
          onValueChange={() => toggleSetting(key)}
          trackColor={{ false: '#e0e0e0', true: '#81b0ff' }}
          thumbColor={settings[key] ? '#2196f3' : '#f4f3f4'}
        />
      )}
    </View>
  );

  const checkForUpdates = () => {
    setShowUpdateModal(true);
  };

  const showAbout = () => {
    Alert.alert('About Sentinel Prime', `Version ${APP_VERSION}\n\nPlatform: ${PLATFORM}\n\nA modular home network security suite.\n\nBuilt with React Native + FastAPI`);
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Settings</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>General</Text>
        {renderSettingItem('Notifications', 'Enable push notifications for alerts', 'notifications')}
        {renderSettingItem('Email Alerts', 'Receive email notifications for critical alerts', 'emailAlerts')}
        {renderSettingItem('Dark Mode', 'Use dark theme', 'darkMode')}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Security</Text>
        {renderSettingItem('Auto Scan', 'Automatically scan new devices on network', 'autoScan')}
        {renderSettingItem('Honeypot', 'Enable honeypot services', 'honeypotEnabled')}
        {renderSettingItem('IPS/IDS', 'Enable intrusion prevention/detection', 'ipsEnabled')}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Network</Text>
        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>Network Range</Text>
            <Text style={styles.settingDescription}>192.168.1.0/24</Text>
          </View>
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>API Server</Text>
            <Text style={styles.settingDescription}>http://localhost:8000</Text>
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data</Text>
        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>Export Data</Text>
            <Text style={styles.settingDescription}>Export all logs and data</Text>
          </View>
        </TouchableOpacity>
        <TouchableOpacity style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>Clear Logs</Text>
            <Text style={styles.settingDescription}>Delete all stored logs</Text>
          </View>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Updates</Text>
        <TouchableOpacity style={styles.settingItem} onPress={checkForUpdates}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>Check for Updates</Text>
            <Text style={styles.settingDescription}>Version {APP_VERSION} - {PLATFORM}</Text>
          </View>
          <Text style={styles.chevron}>›</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.aboutButton} onPress={showAbout}>
        <Text style={styles.aboutButtonText}>About Sentinel Prime</Text>
      </TouchableOpacity>

      <Text style={styles.version}>Version {APP_VERSION}</Text>

      <UpdateCheck visible={showUpdateModal} onClose={() => setShowUpdateModal(false)} />
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
    marginBottom: 20,
    color: '#333',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginHorizontal: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
    paddingHorizontal: 15,
    paddingTop: 15,
    paddingBottom: 8,
    textTransform: 'uppercase',
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  settingInfo: {
    flex: 1,
    marginRight: 10,
  },
  settingTitle: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  settingDescription: {
    fontSize: 13,
    color: '#666',
    marginTop: 2,
  },
  aboutButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginHorizontal: 15,
    marginBottom: 15,
    padding: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  aboutButtonText: {
    fontSize: 16,
    color: '#2196f3',
    fontWeight: '500',
  },
  chevron: {
    fontSize: 24,
    color: '#ccc',
  },
  version: {
    textAlign: 'center',
    color: '#999',
    fontSize: 12,
    marginBottom: 30,
  },
});

export default SettingsScreen;
