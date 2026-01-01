/**
 * FilterPanel Component
 *
 * Dropdowns for filtering tasks by status, priority, and category
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { FilterOptions } from './TaskList';
import './FilterPanel.css';

interface FilterPanelProps {
  filters: FilterOptions;
  onChange: (filters: FilterOptions) => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onChange }) => {
  const { t } = useTranslation();
  const handleFilterChange = (key: keyof FilterOptions, value: string) => {
    onChange({
      ...filters,
      [key]: value === 'all' || value === '' ? undefined : value
    });
  };

  return (
    <div className="filter-panel">
      <div className="filter-group">
        <label>{t('tasks.filter.status')}</label>
        <select
          value={filters.status || 'all'}
          onChange={(e) => handleFilterChange('status', e.target.value)}
        >
          <option value="all">{t('tasks.filter.all')}</option>
          <option value="pending">{t('tasks.filter.pending')}</option>
          <option value="completed">{t('tasks.filter.completed')}</option>
        </select>
      </div>

      <div className="filter-group">
        <label>{t('tasks.filter.priority')}</label>
        <select
          value={filters.priority || 'all'}
          onChange={(e) => handleFilterChange('priority', e.target.value)}
        >
          <option value="all">{t('tasks.filter.all')}</option>
          <option value="high">{t('tasks.filter.high')}</option>
          <option value="medium">{t('tasks.filter.medium')}</option>
          <option value="low">{t('tasks.filter.low')}</option>
        </select>
      </div>

      <div className="filter-group">
        <label>{t('tasks.filter.category')}</label>
        <select
          value={filters.category || ''}
          onChange={(e) => handleFilterChange('category', e.target.value)}
        >
          <option value="">{t('tasks.filter.all')}</option>
          <option value="work">{t('tasks.categories.work')}</option>
          <option value="home">{t('tasks.categories.home')}</option>
          <option value="study">{t('tasks.categories.study')}</option>
          <option value="shopping">{t('tasks.categories.shopping')}</option>
          <option value="health">{t('tasks.categories.health')}</option>
          <option value="fitness">{t('tasks.categories.fitness')}</option>
          <option value="personal">{t('tasks.categories.personal')}</option>
        </select>
      </div>
    </div>
  );
};

export default FilterPanel;
