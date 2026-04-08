import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import ThemeToggle from './ThemeToggle';
import UserMenu from './UserMenu';
import LoginModal from '../auth/LoginModal';

const Header: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [showLogin, setShowLogin] = useState(false);

  return (
    <>
      <header className="darkmoor-header">
        <div className="header-content">
          <div className="logo">
            <span className="brain-icon">🧠</span>
            <h1>DarkmoorAI</h1>
            <span className="beta">BETA</span>
          </div>
          <div className="header-actions">
            <ThemeToggle />
            {isAuthenticated ? (
              <UserMenu />
            ) : (
              <button className="login-btn" onClick={() => setShowLogin(true)}>
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>
      
      <LoginModal isOpen={showLogin} onClose={() => setShowLogin(false)} />
    </>
  );
};

export default Header;