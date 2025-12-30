/**
 * Main App Component
 *
 * Routes and application shell for Phase III Smart Todo ChatKit App
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { SignupPage } from './pages/SignupPage';
import { SigninPage } from './pages/SigninPage';
import SmartTodoApp from "./pages/SmartTodoApp";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="App">
          <Routes>
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/signin" element={<SigninPage />} />
            <Route
              path="/"
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
  );
}

export default App;
