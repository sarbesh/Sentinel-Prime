import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import ApiService from '../services/api';

const DashboardScreen = () => {
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [devicesData, alertsData] = await Promise.all([
        ApiService.getDevices(),
        ApiService.getAlerts(),
      ]);
      setDevices(devicesData);
      setAlerts(alertsData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const onlineDevices = devices.filter(d => d.status === 'online').length;
  const unacknowledgedAlerts = alerts.filter(a => !a.acknowledged).length;
  const criticalAlerts = alerts.filter(a => a.severity === 'critical' && !a.acknowledged).length;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.title}>Dashboard</Text>
      <Text style={styles.subtitle}>Sentinel Prime Security Overview</Text>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{devices.length}</Text>
          <Text style={styles.statLabel}>Total Devices</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statNumber, styles.onlineColor]}>{onlineDevices}</Text>
          <Text style={styles.statLabel}>Online</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statNumber, styles.alertColor]}>{unacknowledgedAlerts}</Text>
          <Text style={styles.statLabel}>Pending Alerts</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statNumber, styles.criticalColor]}>{criticalAlerts}</Text>
          <Text style={styles.statLabel}>Critical</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Alerts</Text>
        {alerts.length === 0 ? (
          <Text style={styles.emptyText}>No alerts yet</Text>
        ) : (
          alerts.slice(0, 5).map(alert => (
            <View key={alert.id} style={[styles.alertItem, getAlertStyle(alert.severity)]}>
              <Text style={styles.alertTitle}>{alert.title}</Text>
              <Text style={styles.alertSource}>{alert.source}</Text>
              <Text style={styles.alertTime}>{new Date(alert.timestamp).toLocaleString()}</Text>
            </View>
          ))
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Devices</Text>
        {devices.length === 0 ? (
          <Text style={styles.emptyText}>No devices found</Text>
        ) : (
          devices.slice(0, 5).map(device => (
            <View key={device.id} style={styles.deviceItem}>
              <View style={styles.deviceInfo}>
                <Text style={styles.deviceName}>{device.name}</Text>
                <Text style={styles.deviceIp}>{device.ip_address}</Text>
              </View>
              <View style={[styles.statusBadge, device.status === 'online' ? styles.onlineBadge : styles.offlineBadge]}>
                <Text style={styles.statusText}>{device.status}</Text>
              </View>
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
};

const getAlertStyle = (severity) => {
  switch (severity) {
    case 'critical':
      return styles.criticalAlert;
    case 'high':
      return styles.highAlert;
    case 'medium':
      return styles.mediumAlert;
    default:
      return styles.lowAlert;
  }
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
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    marginBottom: 20,
  },
  statCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    width: '48%',
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  onlineColor: {
    color: '#4caf50',
  },
  alertColor: {
    color: '#ff9800',
  },
  criticalColor: {
    color: '#f44336',
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
  emptyText: {
    color: '#999',
    textAlign: 'center',
    paddingVertical: 20,
  },
  alertItem: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  criticalAlert: {
    backgroundColor: '#ffebee',
    borderLeftWidth: 4,
    borderLeftColor: '#f44336',
  },
  highAlert: {
    backgroundColor: '#fff3e0',
    borderLeftWidth: 4,
    borderLeftColor: '#ff9800',
  },
  mediumAlert: {
    backgroundColor: '#fff8e1',
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  lowAlert: {
    backgroundColor: '#e8f5e9',
    borderLeftWidth: 4,
    borderLeftColor: '#4caf50',
  },
  alertTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  alertSource: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  alertTime: {
    fontSize: 11,
    color: '#999',
    marginTop: 4,
  },
  deviceItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f9f9f9',
    marginBottom: 10,
  },
  deviceInfo: {
    flex: 1,
  },
  deviceName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  deviceIp: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  onlineBadge: {
    backgroundColor: '#e8f5e9',
  },
  offlineBadge: {
    backgroundColor: '#ffebee',
  },
  statusText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
});

export default DashboardScreen;
