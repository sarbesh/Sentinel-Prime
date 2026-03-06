import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Modal, Alert, RefreshControl } from 'react-native';
import ApiService from '../services/api';

const SNOOZE_OPTIONS = [
  { label: '1 hour', value: 1/24 },
  { label: 'Tomorrow', value: 1 },
  { label: '3 days', value: 3 },
  { label: '1 week', value: 7 },
];

const TodoScreen = () => {
  const [todos, setTodos] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showSnoozeModal, setShowSnoozeModal] = useState(false);
  const [selectedTodo, setSelectedTodo] = useState(null);
  const [newTodo, setNewTodo] = useState({ title: '', description: '', priority: 'medium' });
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      const data = await ApiService.request('/todos');
      setTodos(data);
    } catch (error) {
      console.error('Error fetching todos:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchTodos();
    setRefreshing(false);
  };

  const addTodo = async () => {
    if (!newTodo.title.trim()) {
      Alert.alert('Error', 'Please enter a title');
      return;
    }
    try {
      await ApiService.request('/todos', {
        method: 'POST',
        body: newTodo,
      });
      setShowAddModal(false);
      setNewTodo({ title: '', description: '', priority: 'medium' });
      fetchTodos();
    } catch (error) {
      Alert.alert('Error', 'Failed to add todo');
    }
  };

  const toggleComplete = async (todo) => {
    try {
      await ApiService.request(`/todos/${todo.id}/complete`, {
        method: 'POST',
      });
      fetchTodos();
    } catch (error) {
      Alert.alert('Error', 'Failed to complete todo');
    }
  };

  const deleteTodo = async (todoId) => {
    Alert.alert('Delete Todo', 'Are you sure you want to delete this todo?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Delete', style: 'destructive', onPress: async () => {
        try {
          await ApiService.request(`/todos/${todoId}`, { method: 'DELETE' });
          fetchTodos();
        } catch (error) {
          Alert.alert('Error', 'Failed to delete todo');
        }
      }},
    ]);
  };

  const snoozeTodo = async (days) => {
    if (!selectedTodo) return;
    try {
      await ApiService.request(`/todos/${selectedTodo.id}/snooze?days=${days}`, {
        method: 'POST',
      });
      setShowSnoozeModal(false);
      setSelectedTodo(null);
      fetchTodos();
      Alert.alert('Snoozed', `Todo snoozed for ${days} day(s)`);
    } catch (error) {
      Alert.alert('Error', 'Failed to snooze todo');
    }
  };

  const openSnoozeModal = (todo) => {
    setSelectedTodo(todo);
    setShowSnoozeModal(true);
  };

  const filteredTodos = todos.filter(todo => {
    const now = new Date();
    if (todo.snoozed_until && new Date(todo.snoozed_until) > now) {
      return false;
    }
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true;
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#2196f3';
      case 'low': return '#4caf50';
      default: return '#999';
    }
  };

  const renderTodoItem = (todo) => (
    <View key={todo.id} style={[styles.todoItem, todo.completed && styles.completedItem]}>
      <TouchableOpacity style={styles.checkbox} onPress={() => toggleComplete(todo)}>
        <Text style={[styles.checkboxIcon, todo.completed && styles.checkboxChecked]}>
          {todo.completed ? '✓' : '○'}
        </Text>
      </TouchableOpacity>
      <View style={styles.todoContent}>
        <Text style={[styles.todoTitle, todo.completed && styles.completedText]}>{todo.title}</Text>
        {todo.description && (
          <Text style={styles.todoDescription}>{todo.description}</Text>
        )}
        <View style={styles.todoMeta}>
          <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(todo.priority) }]}>
            <Text style={styles.priorityText}>{todo.priority}</Text>
          </View>
          {todo.category && <Text style={styles.categoryText}>{todo.category}</Text>}
        </View>
      </View>
      <View style={styles.todoActions}>
        {!todo.completed && (
          <TouchableOpacity style={styles.actionButton} onPress={() => openSnoozeModal(todo)}>
            <Text style={styles.actionIcon}>⏰</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity style={styles.actionButton} onPress={() => deleteTodo(todo.id)}>
          <Text style={styles.actionIcon}>🗑️</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <Text style={styles.title}>Todos</Text>
      <Text style={styles.subtitle}>Manage your tasks</Text>

      <View style={styles.filterContainer}>
        {['all', 'active', 'completed'].map(f => (
          <TouchableOpacity
            key={f}
            style={[styles.filterButton, filter === f && styles.filterButtonActive]}
            onPress={() => setFilter(f)}
          >
            <Text style={[styles.filterText, filter === f && styles.filterTextActive]}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{todos.filter(t => !t.completed).length}</Text>
          <Text style={styles.statLabel}>Active</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statNumber, styles.completedNumber]}>{todos.filter(t => t.completed).length}</Text>
          <Text style={styles.statLabel}>Completed</Text>
        </View>
      </View>

      <View style={styles.todoList}>
        {filteredTodos.length === 0 ? (
          <Text style={styles.emptyText}>No todos found</Text>
        ) : (
          filteredTodos.map(renderTodoItem)
        )}
      </View>

      <TouchableOpacity style={styles.addButton} onPress={() => setShowAddModal(true)}>
        <Text style={styles.addButtonText}>+ Add Todo</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>Sentinel Prime Todos</Text>

      {/* Add Todo Modal */}
      <Modal visible={showAddModal} transparent animationType="slide" onRequestClose={() => setShowAddModal(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add New Todo</Text>
            <TextInput
              style={styles.input}
              placeholder="Title"
              value={newTodo.title}
              onChangeText={(text) => setNewTodo({ ...newTodo, title: text })}
            />
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Description (optional)"
              value={newTodo.description}
              onChangeText={(text) => setNewTodo({ ...newTodo, description: text })}
              multiline
            />
            <Text style={styles.inputLabel}>Priority</Text>
            <View style={styles.priorityContainer}>
              {['low', 'medium', 'high', 'urgent'].map(p => (
                <TouchableOpacity
                  key={p}
                  style={[styles.priorityOption, newTodo.priority === p && styles.priorityOptionActive]}
                  onPress={() => setNewTodo({ ...newTodo, priority: p })}
                >
                  <Text style={[styles.priorityOptionText, { color: getPriorityColor(p) }]}>{p}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setShowAddModal(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.submitButton} onPress={addTodo}>
                <Text style={styles.submitButtonText}>Add</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Snooze Modal */}
      <Modal visible={showSnoozeModal} transparent animationType="slide" onRequestClose={() => setShowSnoozeModal(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Remind Me Later</Text>
            <Text style={styles.snoozeSubtitle}>Snooze this todo until:</Text>
            {SNOOZE_OPTIONS.map(option => (
              <TouchableOpacity
                key={option.label}
                style={styles.snoozeOption}
                onPress={() => snoozeTodo(option.value)}
              >
                <Text style={styles.snoozeOptionText}>{option.label}</Text>
              </TouchableOpacity>
            ))}
            <TouchableOpacity style={styles.cancelButton} onPress={() => setShowSnoozeModal(false)}>
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  title: { fontSize: 28, fontWeight: 'bold', marginTop: 50, marginHorizontal: 20, color: '#333' },
  subtitle: { fontSize: 14, color: '#666', marginHorizontal: 20, marginBottom: 20 },
  filterContainer: { flexDirection: 'row', marginHorizontal: 15, marginBottom: 15 },
  filterButton: { flex: 1, padding: 10, alignItems: 'center', backgroundColor: '#fff', marginHorizontal: 2, borderRadius: 8 },
  filterButtonActive: { backgroundColor: '#2196f3' },
  filterText: { fontSize: 14, color: '#666' },
  filterTextActive: { color: '#fff', fontWeight: 'bold' },
  statsContainer: { flexDirection: 'row', marginHorizontal: 15, marginBottom: 15 },
  statCard: { flex: 1, backgroundColor: '#fff', borderRadius: 12, padding: 15, marginHorizontal: 5, alignItems: 'center' },
  statNumber: { fontSize: 28, fontWeight: 'bold', color: '#2196f3' },
  completedNumber: { color: '#4caf50' },
  statLabel: { fontSize: 12, color: '#666', marginTop: 5 },
  todoList: { marginHorizontal: 15 },
  todoItem: { flexDirection: 'row', backgroundColor: '#fff', borderRadius: 12, padding: 15, marginBottom: 10, alignItems: 'flex-start' },
  completedItem: { opacity: 0.6 },
  checkbox: { marginRight: 12, padding: 5 },
  checkboxIcon: { fontSize: 20, color: '#999' },
  checkboxChecked: { color: '#4caf50' },
  todoContent: { flex: 1 },
  todoTitle: { fontSize: 16, fontWeight: 'bold', color: '#333' },
  completedText: { textDecorationLine: 'line-through', color: '#999' },
  todoDescription: { fontSize: 13, color: '#666', marginTop: 4 },
  todoMeta: { flexDirection: 'row', marginTop: 8, alignItems: 'center' },
  priorityBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8, marginRight: 8 },
  priorityText: { fontSize: 10, color: '#fff', fontWeight: 'bold', textTransform: 'uppercase' },
  categoryText: { fontSize: 11, color: '#999' },
  todoActions: { flexDirection: 'row' },
  actionButton: { padding: 5, marginLeft: 5 },
  actionIcon: { fontSize: 18 },
  emptyText: { textAlign: 'center', color: '#999', padding: 30 },
  addButton: { backgroundColor: '#2196f3', marginHorizontal: 15, marginVertical: 20, padding: 15, borderRadius: 12, alignItems: 'center' },
  addButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  footer: { textAlign: 'center', color: '#ccc', fontSize: 12, marginBottom: 40 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' },
  modalContent: { backgroundColor: '#fff', borderRadius: 16, padding: 20, width: '90%', maxWidth: 400 },
  modalTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' },
  input: { backgroundColor: '#f5f5f5', borderRadius: 8, padding: 12, marginBottom: 12, fontSize: 16 },
  textArea: { minHeight: 80, textAlignVertical: 'top' },
  inputLabel: { fontSize: 14, color: '#666', marginBottom: 8 },
  priorityContainer: { flexDirection: 'row', marginBottom: 20 },
  priorityOption: { flex: 1, padding: 10, alignItems: 'center', marginHorizontal: 2, borderRadius: 8, borderWidth: 1, borderColor: '#ddd' },
  priorityOptionActive: { backgroundColor: '#e3f2fd', borderColor: '#2196f3' },
  priorityOptionText: { fontWeight: 'bold', textTransform: 'uppercase', fontSize: 12 },
  modalButtons: { flexDirection: 'row', marginTop: 10 },
  cancelButton: { flex: 1, padding: 12, alignItems: 'center', marginRight: 5, borderRadius: 8, backgroundColor: '#f5f5f5' },
  cancelButtonText: { color: '#666', fontSize: 16 },
  submitButton: { flex: 1, padding: 12, alignItems: 'center', marginLeft: 5, borderRadius: 8, backgroundColor: '#2196f3' },
  submitButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  snoozeSubtitle: { fontSize: 14, color: '#666', marginBottom: 15, textAlign: 'center' },
  snoozeOption: { padding: 15, borderBottomWidth: 1, borderBottomColor: '#eee' },
  snoozeOptionText: { fontSize: 16, color: '#333', textAlign: 'center' },
});

export default TodoScreen;
