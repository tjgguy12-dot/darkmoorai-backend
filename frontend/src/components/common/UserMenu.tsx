import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const UserMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  return (
    <div className="user-menu" ref={menuRef}>
      <button className="user-menu-trigger" onClick={() => setIsOpen(!isOpen)}>
        <span className="user-avatar">{user.username?.[0]?.toUpperCase() || '👤'}</span>
        <span className="user-name">{user.username || user.email}</span>
      </button>
      
      {isOpen && (
        <div className="user-menu-dropdown">
          <div className="user-info">
            <strong>{user.full_name || user.username}</strong>
            <span>{user.email}</span>
          </div>
          <div className="user-menu-divider" />
          <button className="user-menu-item" onClick={logout}>
            <span>🚪</span> Sign Out
          </button>
        </div>
      )}
    </div>
  );
};

export default UserMenu;