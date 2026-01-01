/**
 * TaskCard Component
 *
 * Displays a single task with all metadata:
 * - Priority badge (color-coded)
 * - Category tag
 * - Due date
 * - Recurring indicator
 * - Complete/delete actions
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import './TaskCard.css';

export interface Task {
  id: number;
  title: string;
  description?: string;
  priority: 'high' | 'medium' | 'low';
  category?: string;
  due_date?: string;
  completed: boolean;
  is_recurring?: boolean;
  recurrence_pattern?: 'daily' | 'weekly' | 'monthly';
  created_at: string;
}

interface TaskCardProps {
  task: Task;
  onComplete?: (taskId: number) => void;
  onDelete?: (taskId: number) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onComplete, onDelete }) => {
  const { t } = useTranslation();
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isOverdue = (dateString?: string) => {
    if (!dateString) return false;
    return new Date(dateString) < new Date() && !task.completed;
  };

  const priorityColors = {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#10b981'
  };

  const categoryColors: Record<string, string> = {
    work: '#3b82f6',
    home: '#8b5cf6',
    study: '#06b6d4',
    shopping: '#ec4899',
    health: '#10b981',
    fitness: '#f97316',
    personal: '#6366f1'
  };

  return (
    <div className={`task-card ${task.completed ? 'completed' : ''}`}>
      <div className="task-header">
        <div className="task-meta">
          {/* Priority Badge */}
          <span
            className="priority-badge"
            style={{ backgroundColor: priorityColors[task.priority] }}
          >
            {task.priority === 'high' ? t('tasks.filter.high') : task.priority === 'medium' ? t('tasks.filter.medium') : t('tasks.filter.low')}
          </span>

          {/* Category Tag */}
          {task.category && (
            <span
              className="category-tag"
              style={{
                backgroundColor: categoryColors[task.category] || '#6b7280',
                color: 'white'
              }}
            >
              {t(`tasks.categories.${task.category}`, { defaultValue: task.category })}
            </span>
          )}

          {/* Recurring Indicator */}
          {task.is_recurring && (
            <span className="recurring-badge" title={`${t('tasks.card.recurring')}: ${task.recurrence_pattern}`}>
              🔄 {task.recurrence_pattern}
            </span>
          )}
        </div>

        {/* Actions */}
        <div className="task-actions">
          {!task.completed && onComplete && (
            <button
              className="btn-complete"
              onClick={() => onComplete(task.id)}
              title={t('tasks.card.complete')}
            >
              ✓
            </button>
          )}
          {onDelete && (
            <button
              className="btn-delete"
              onClick={() => onDelete(task.id)}
              title={t('tasks.card.delete')}
            >
              ×
            </button>
          )}
        </div>
      </div>

      <div className="task-content">
        <h3 className="task-title">{task.title}</h3>
        {task.description && (
          <p className="task-description">{task.description}</p>
        )}

        {/* Due Date */}
        {task.due_date && (
          <div className={`task-due-date ${isOverdue(task.due_date) ? 'overdue' : ''}`}>
            <span className="due-icon">📅</span>
            <span>{formatDate(task.due_date)}</span>
            {isOverdue(task.due_date) && <span className="overdue-label">OVERDUE</span>}
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskCard;
