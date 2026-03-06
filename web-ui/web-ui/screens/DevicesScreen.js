import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Modal, TextInput, Alert, RefreshControl } from 'react-native';
import ApiService from '../services/api';

const DEVICE_TYPES = ['unknown', 'router', 'computer', 'laptop', 'phone', 'tablet', 'iot', 'server', 'tv', 'printer', 'gaming', 'other'];
const DEVICE_STATUSES = ['online', 'offline', 'unknown'];

const DevicesScreen = () => {
  const [devices, setDevices] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingDevice, setEditingDevice] = useState(null);
  const [formData, setFormData] = useState({ name: '', ip_address: '', mac_address: '', type: 'unknown', status: 'unknown' });
  const [refreshing, setRefreshing] = useState(false);

  const fetchDevices = async () => {
    try {
      const data = await ApiService.getDevices();
      setDevices(data);
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchDevices();
    setRefreshing(false);
  };

  const openAddModal = () => {
    setEditingDevice(null);
    setFormData({ name: '', ip_address: '', mac_address: '', type: 'unknown', status: 'unknown' });
    setModalVisible(true);
  };

  const openEditModal = (device) => {
    setEditingDevice(device);
    setFormData({
      name: device.name,
      ip_address: device.ip_address,
      mac_address: device.mac_address || '',
      type: device.type,
      status: device.status,
    });
    setModalVisible(true);
  };

  const handleSave = async () => {
    if (!formData.name || !formData.ip_address) {
      Alert.alert('Error', 'Name and IP address are required');
      return;
    }

    try {
      if (editingDevice) {
        await ApiService.updateDevice(editingDevice.id, formData);
      } else {
        await ApiService.createDevice(formData);
      }
      setModalVisible(false);
      fetchDevices();
    } catch (error) {
      Alert.alert('Error', 'Failed to save device');
    }
  };

  const handleDelete = (device) => {
    Alert.alert('Delete Device', `Are you sure you want to delete ${device.name}?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await ApiService.deleteDevice(device.id);
            fetchDevices();
          } catch (error) {
            Alert.alert('Error', 'Failed to delete device');
          }
        },
      },
    ]);
  };

  const renderDevice = ({ item }) => (
    <TouchableOpacity style={styles.deviceCard} onPress={() => openEditModal(item)}>
      <View style={styles.deviceInfo}>
        <Text style={styles.deviceName}>{item.name}</Text>
        <Text style={styles.deviceIp}>{item.ip_address}</Text>
        {item.mac_address && <Text style={styles.deviceMac}>MAC: {item.mac_address}</Text>}
        <View style={styles.badges}>
          <View style={styles.typeBadge}><Text style={styles.badgeText}>{item.type}</Text></View>
        </View>
      </View>
      <View style={styles.deviceActions}>
        <View style={[styles.statusBadge, item.status === 'online' ? styles.onlineBadge : styles.offlineBadge]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
        <TouchableOpacity style={styles.deleteButton} onPress={() => handleDelete(item)}>
          <Text style={styles.deleteText}>Delete</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Devices</Text>
      <TouchableOpacity style={styles.addButton} onPress={openAddModal}>
        <Text style={styles.addButtonText}>+ Add Device</Text>
      </TouchableOpacity>

      <FlatList
        data={devices}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderDevice}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.emptyText}>No devices found</Text>}
        contentContainerStyle={styles.listContent}
      />

      <Modal visible={modalVisible} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{editingDevice ? 'Edit Device' : 'Add Device'}</Text>
            
            <Text style={styles.inputLabel}>Name *</Text>
            <TextInput style={styles.input} value={formData.name} onChangeText={(text) => setFormData({...formData, name: text})} placeholder="Device name" />
            
            <Text style={styles.inputLabel}>IP Address *</Text>
            <TextInput style={styles.input} value={formData.ip_address} onChangeText={(text) => setFormData({...formData, ip_address: text})} placeholder="192.168.1.1" keyboardType="numeric" />
            
            <Text style={styles.inputLabel}>MAC Address</Text>
            <TextInput style={styles.input} value={formData.mac_address} onChangeText={(text) => setFormData({...formData, mac_address: text})} placeholder="AA:BB:CC:DD:EE:FF" />
            
            <Text style={styles.inputLabel}>Type</Text>
            <View style={styles.typeSelector}>
              {DEVICE_TYPES.map(type => (
                <TouchableOpacity key={type} style={[styles.typeOption, formData.type === type && styles.typeOptionSelected]} onPress={() => setFormData({...formData, type})}>
                  <Text style={[styles.typeOptionText, formData.type === type && styles.typeOptionTextSelected]}>{type}</Text>
                </TouchableOpacity>
              ))}
            </View>
            
            <Text style={styles.inputLabel}>Status</Text>
            <View style={styles.statusSelector}>
              {DEVICE_STATUSES.map(status => (
                <TouchableOpacity key={status} style={[styles.statusOption, formData.status === status && styles.statusOptionSelected]} onPress={() => setFormData({...formData, status})}>
                  <Text style={[styles.statusOptionText, formData.status === status && styles.statusOptionTextSelected]}>{status}</Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setModalVisible(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
                <Text style={styles.saveButtonText}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
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
  addButton: {
    backgroundColor: '#2196f3',
    marginHorizontal: 20,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  listContent: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  deviceCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  deviceInfo: {
    flex: 1,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  deviceIp: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  deviceMac: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  badges: {
    flexDirection: 'row',
    marginTop: 8,
  },
  typeBadge: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  badgeText: {
    fontSize: 11,
    color: '#1976d2',
  },
  deviceActions: {
    alignItems: 'flex-end',
    justifyContent: 'space-between',
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
  deleteButton: {
    marginTop: 10,
    padding: 5,
  },
  deleteText: {
    color: '#f44336',
    fontSize: 12,
  },
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 50,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    width: '90%',
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 5,
    marginTop: 10,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
  },
  typeSelector: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 5,
  },
  typeOption: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    marginBottom: 5,
  },
  typeOptionSelected: {
    backgroundColor: '#2196f3',
  },
  typeOptionText: {
    fontSize: 12,
    color: '#333',
  },
  typeOptionTextSelected: {
    color: '#fff',
  },
  statusSelector: {
    flexDirection: 'row',
    gap: 10,
  },
  statusOption: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  statusOptionSelected: {
    backgroundColor: '#4caf50',
  },
  statusOptionText: {
    fontSize: 14,
    color: '#333',
  },
  statusOptionTextSelected: {
    color: '#fff',
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
    gap: 10,
  },
  cancelButton: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    color: '#666',
  },
  saveButton: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    backgroundColor: '#2196f3',
    alignItems: 'center',
  },
  saveButtonText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default DevicesScreen;
