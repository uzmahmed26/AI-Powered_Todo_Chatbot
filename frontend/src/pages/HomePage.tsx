/**
 * Home/Landing Page
 *
 * Welcome page for the Smart Todo Assistant
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { Navbar } from '../components/Navbar';
import './HomePage.css';

export const HomePage: React.FC = () => {
  const { user, isLoading } = useAuth();
  const { t } = useTranslation();

  return (
    <div className="home-page">
      <Navbar />

      <div className="home-hero">
        <div className="home-hero-content">
          <h1 className="home-hero-title">
            🤖 {t('home.hero.title')}
          </h1>
          <p className="home-hero-subtitle">
            {t('home.hero.subtitle')}
          </p>
          <p className="home-hero-description">
            {t('home.hero.description')}
          </p>

          <div className="home-hero-actions">
            {isLoading ? (
              <div style={{ minHeight: '44px' }}></div>
            ) : user ? (
              <Link to="/app" className="home-btn home-btn-primary">
                {t('home.hero.goToDashboard')}
              </Link>
            ) : (
              <>
                <Link to="/signup" className="home-btn home-btn-primary">
                  {t('home.hero.getStarted')}
                </Link>
                <Link to="/signin" className="home-btn home-btn-secondary">
                  {t('home.hero.signIn')}
                </Link>
              </>
            )}
          </div>
        </div>

        <div className="home-hero-image">
          <div className="home-feature-preview">
            <div className="preview-chat-bubble user">
              💬 "{t('home.preview.user1')}"
            </div>
            <div className="preview-chat-bubble assistant">
              ✅ "{t('home.preview.assistant1')}"
            </div>
            <div className="preview-chat-bubble user">
              💬 "{t('home.preview.user2')}"
            </div>
            <div className="preview-chat-bubble assistant">
              📋 "{t('home.preview.assistant2')}"
            </div>
          </div>
        </div>
      </div>

      <div className="home-features">
        <div className="home-section-title">
          <h2>{t('home.features.title')}</h2>
          <p>{t('home.features.subtitle')}</p>
        </div>

        <div className="home-features-grid">
          <div className="home-feature-card">
            <div className="feature-icon">🗣️</div>
            <h3>{t('home.features.naturalLanguage.title')}</h3>
            <p>{t('home.features.naturalLanguage.description')}</p>
          </div>

          <div className="home-feature-card">
            <div className="feature-icon">🌍</div>
            <h3>{t('home.features.multiLanguage.title')}</h3>
            <p>{t('home.features.multiLanguage.description')}</p>
          </div>

          <div className="home-feature-card">
            <div className="feature-icon">🎤</div>
            <h3>{t('home.features.voiceInput.title')}</h3>
            <p>{t('home.features.voiceInput.description')}</p>
          </div>

          <div className="home-feature-card">
            <div className="feature-icon">🔄</div>
            <h3>{t('home.features.recurringTasks.title')}</h3>
            <p>{t('home.features.recurringTasks.description')}</p>
          </div>

          <div className="home-feature-card">
            <div className="feature-icon">🔍</div>
            <h3>{t('home.features.smartSearch.title')}</h3>
            <p>{t('home.features.smartSearch.description')}</p>
          </div>

          <div className="home-feature-card">
            <div className="feature-icon">⚡</div>
            <h3>{t('home.features.aiPowered.title')}</h3>
            <p>{t('home.features.aiPowered.description')}</p>
          </div>
        </div>
      </div>

      <div className="home-cta">
        <h2>{t('home.cta.title')}</h2>
        <p>{t('home.cta.subtitle')}</p>
        {!isLoading && !user && (
          <Link to="/signup" className="home-btn home-btn-primary home-btn-large">
            {t('home.cta.button')}
          </Link>
        )}
      </div>

      <footer className="home-footer">
        <p>{t('home.footer.text')}</p>
      </footer>
    </div>
  );
};
