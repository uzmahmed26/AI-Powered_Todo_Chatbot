/**
 * SortSelector Component
 *
 * Dropdown for sorting tasks by different criteria
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { SortOptions } from './TaskList';
import './SortSelector.css';

interface SortSelectorProps {
  sort: SortOptions;
  onChange: (sort: SortOptions) => void;
}

const SortSelector: React.FC<SortSelectorProps> = ({ sort, onChange }) => {
  const { t } = useTranslation();
  const handleSortByChange = (sortBy: SortOptions['sortBy']) => {
    onChange({ ...sort, sortBy });
  };

  const handleSortOrderChange = () => {
    onChange({
      ...sort,
      sortOrder: sort.sortOrder === 'asc' ? 'desc' : 'asc'
    });
  };

  return (
    <div className="sort-selector">
      <label>{t('tasks.sort.label')}</label>
      <select
        value={sort.sortBy}
        onChange={(e) => handleSortByChange(e.target.value as SortOptions['sortBy'])}
      >
        <option value="due_date">{t('tasks.sort.dueDate')}</option>
        <option value="priority">{t('tasks.sort.priority')}</option>
        <option value="title">{t('tasks.sort.title')}</option>
      </select>

      <button
        className="sort-order-btn"
        onClick={handleSortOrderChange}
        title={sort.sortOrder === 'asc' ? 'Sort descending' : 'Sort ascending'}
      >
        {sort.sortOrder === 'asc' ? '↑' : '↓'}
      </button>
    </div>
  );
};

export default SortSelector;
