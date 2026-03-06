import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert as RNAlert, RefreshControl } from 'react-native';
import ApiService from '../services/api';

const AlertsScreen = () => {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [refreshing, setRefreshing] = useState(false);

  const fetchAlerts = async () => {
    try {
      const acknowledged = filter === 'all' ? null : filter === 'acknowledged';
      const data = await ApiService.getAlerts(acknowledged);
      setAlerts(data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [filter]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchAlerts();
    setRefreshing(false);
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await ApiService.acknowledgeAlert(alertId);
      fetchAlerts();
    } catch (error) {
      RNAlert.alert('Error', 'Failed to acknowledge alert');
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#ffc107';
      default: return '#4caf50';
    }
  };

  const getSeverityBgColor = (severity) => {
    switch (severity) {
      case 'critical': return '#ffebee';
      case 'high': return '#fff3e0';
      case 'medium': return '#fff8e1';
      default: return '#e8f5e9';
    }
  };

  const renderAlert = ({ item }) => (
    <View style={[styles.alertCard, { backgroundColor: getSeverityBgColor(item.severity) }]}>
      <View style={styles.alertHeader}>
        <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(item.severity) }]}>
          <Text style={styles.severityText}>{item.severity.toUpperCase()}</Text>
        </View>
        <Text style={styles.alertTime}>{new Date(item.timestamp).toLocaleString()}</Text>
      </View>
      <Text style={styles.alertTitle}>{item.title}</Text>
      <Text style={styles.alertSource}>Source: {item.source}</Text>
      {item.description && <Text style={styles.alertDescription}>{item.description}</Text>}
      {item.acknowledged ? (
        <View style={styles.acknowledgedBadge}>
          <Text style={styles.acknowledgedText}>Acknowledged</Text>
        </View>
      ) : (
        <TouchableOpacity style={styles.acknowledgeButton} onPress={() => handleAcknowledge(item.id)}>
          <Text style={styles.acknowledgeButtonText}>Acknowledge</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Alerts</Text>
      
      <View style={styles.filterContainer}>
        <TouchableOpacity style={[styles.filterButton, filter === 'all' && styles.filterButtonActive]} onPress={() => setFilter('all')}>
          <Text style={[styles.filterText, filter === 'all' && styles.filterTextActive]}>All</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.filterButton, filter === 'pending' && styles.filterButtonActive]} onPress={() => setFilter('pending')}>
          <Text style={[styles.filterText, filter === 'pending' && styles.filterTextActive]}>Pending</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.filterButton, filter === 'acknowledged' && styles.filterButtonActive]} onPress={() => setFilter('acknowledged')}>
          <Text style={[styles.filterText, filter === 'acknowledged' && styles.filterTextActive]}>Acknowledged</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={alerts}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderAlert}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.emptyText}>No alerts found</Text>}
        contentContainerStyle={styles.listContent}
      />
    </View>
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
    marginBottom: 15,
    color: '#333',
  },
  filterContainer: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginBottom: 15,
    gap: 10,
  },
  filterButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: '#fff',
    alignItems: 'center',
  },
  filterButtonActive: {
    backgroundColor: '#2196f3',
  },
  filterText: {
    fontSize: 14,
    color: '#666',
    fontWeight: 'bold',
  },
  filterTextActive: {
    color: '#fff',
  },
  listContent: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  alertCard: {
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  severityText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  alertTime: {
    fontSize: 11,
    color: '#666',
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  alertSource: {
    fontSize: 13,
    color: '#666',
  },
  alertDescription: {
    fontSize: 13,
    color: '#555',
    marginTop: 8,
  },
  acknowledgeButton: {
    marginTop: 12,
    backgroundColor: '#2196f3',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  acknowledgeButtonText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
  },
  acknowledgedBadge: {
    marginTop: 12,
    backgroundColor: '#4caf50',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  acknowledgedText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 50,
  },
});

export default AlertsScreen;
