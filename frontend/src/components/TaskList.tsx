/**
 * TaskList Component
 *
 * Displays a list of tasks with search, filter, and sort capabilities
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import TaskCard, { Task } from './TaskCard';
import SearchBar from './SearchBar';
import FilterPanel from './FilterPanel';
import SortSelector from './SortSelector';
import { apiClient } from '../services/api';
import './TaskList.css';

interface TaskListProps {
  userId: string;
}

export interface FilterOptions {
  status?: 'pending' | 'completed' | 'all';
  priority?: 'high' | 'medium' | 'low' | 'all';
  category?: string;
}

export interface SortOptions {
  sortBy: 'due_date' | 'priority' | 'title';
  sortOrder: 'asc' | 'desc';
}

const TaskList: React.FC<TaskListProps> = ({ userId }) => {
  const { t } = useTranslation();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({
    status: 'all',
    priority: 'all',
    category: undefined
  });
  const [sort, setSort] = useState<SortOptions>({
    sortBy: 'due_date',
    sortOrder: 'asc'
  });

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.listTasks(userId, {
        search: searchQuery || undefined,
        status: filters.status !== 'all' ? filters.status : undefined,
        priority: filters.priority !== 'all' ? filters.priority : undefined,
        category: filters.category,
        sort_by: sort.sortBy,
        sort_order: sort.sortOrder
      });

      setTasks(response.tasks || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  // Fetch on mount and when filters change
  useEffect(() => {
    if (userId) {
      fetchTasks();
    }
  }, [userId, searchQuery, filters, sort]);

  // Handle complete task
  const handleCompleteTask = async (taskId: number) => {
    try {
      await apiClient.completeTask(userId, taskId);
      fetchTasks(); // Refresh list
    } catch (err: any) {
      setError(err.message || 'Failed to complete task');
    }
  };

  // Handle delete task
  const handleDeleteTask = async (taskId: number) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await apiClient.deleteTask(userId, taskId);
      fetchTasks(); // Refresh list
    } catch (err: any) {
      setError(err.message || 'Failed to delete task');
    }
  };

  return (
    <div className="task-list-container">
      {/* Search & Controls */}
      <div className="task-controls">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search tasks..."
        />

        <div className="controls-row">
          <FilterPanel
            filters={filters}
            onChange={setFilters}
          />

          <SortSelector
            sort={sort}
            onChange={setSort}
          />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading tasks...</p>
        </div>
      )}

      {/* Tasks List */}
      {!loading && tasks.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">{t('tasks.empty.icon')}</div>
          <h3>{t('tasks.empty.title')}</h3>
          <p>{t('tasks.empty.description')}</p>
        </div>
      )}

      {!loading && tasks.length > 0 && (
        <div className="tasks-grid">
          {tasks.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onComplete={handleCompleteTask}
              onDelete={handleDeleteTask}
            />
          ))}
        </div>
      )}

      {/* Task Count */}
      {!loading && tasks.length > 0 && (
        <div className="task-count">
          Showing {tasks.length} task{tasks.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

export default TaskList;
