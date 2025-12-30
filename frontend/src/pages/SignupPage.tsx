import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);

    try {
      await signup(email, password, fullName);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Signup failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f9fafb', padding: '3rem 1rem' }}>
      <div style={{ maxWidth: '28rem', width: '100%' }}>
        <div>
          <h2 style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '1.875rem', fontWeight: 'bold', color: '#111827' }}>
            Create your account
          </h2>
          <p style={{ marginTop: '0.5rem', textAlign: 'center', fontSize: '0.875rem', color: '#6b7280' }}>
            Already have an account?{' '}
            <Link to="/signin" style={{ fontWeight: '500', color: '#4f46e5', textDecoration: 'none' }}>
              Sign in
            </Link>
          </p>
        </div>

        <form style={{ marginTop: '2rem' }} onSubmit={handleSubmit}>
          {error && (
            <div style={{ marginBottom: '1rem', padding: '0.75rem', background: '#fef2f2', borderRadius: '0.375rem', color: '#dc2626', fontSize: '0.875rem' }}>
              {error}
            </div>
          )}

          <div style={{ marginBottom: '1rem' }}>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Full name"
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
            />
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password (min 8 characters)"
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm password"
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', fontSize: '0.875rem' }}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            style={{ width: '100%', padding: '0.75rem', background: isLoading ? '#9ca3af' : '#4f46e5', color: 'white', border: 'none', borderRadius: '0.375rem', fontSize: '0.875rem', fontWeight: '500', cursor: isLoading ? 'not-allowed' : 'pointer' }}
          >
            {isLoading ? 'Creating account...' : 'Sign up'}
          </button>
        </form>
      </div>
    </div>
  );
}
