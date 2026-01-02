/**
 * Main App Component
 *
 * Routes and application shell for Phase III Smart Todo ChatKit App
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { HomePage } from './pages/HomePage';
import { SignupPage } from './pages/SignupPage';
import { SigninPage } from './pages/SigninPage';
import SmartTodoApp from "./pages/SmartTodoApp";
import "./App.css";

function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <AuthProvider>
          <div className="App">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/signin" element={<SigninPage />} />

              {/* Protected Routes */}
              <Route
                path="/app"
                element={
                  <ProtectedRoute>
                    <SmartTodoApp />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </AuthProvider>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
