/**
 * Navbar Component
 *
 * Navigation bar with signin/signup options
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LanguageToggle } from './LanguageToggle';
import './Navbar.css';

export const Navbar: React.FC = () => {
  const { user, signout, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSignout = async () => {
    await signout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🤖 Smart Todo Assistant
        </Link>

        <div className="navbar-menu">
          <LanguageToggle />

          {isLoading ? (
            <div style={{ width: '200px', minHeight: '36px' }}></div>
          ) : user ? (
            <div className="navbar-user">
              <span className="navbar-username">
                {user.full_name || user.email}
              </span>
              <Link to="/app" className="navbar-button navbar-button-primary">
                Dashboard
              </Link>
              <button
                onClick={handleSignout}
                className="navbar-button navbar-button-secondary"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="navbar-auth">
              <Link to="/signin" className="navbar-button navbar-button-secondary">
                Sign In
              </Link>
              <Link to="/signup" className="navbar-button navbar-button-primary">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
