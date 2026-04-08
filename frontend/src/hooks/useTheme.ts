import { useState, useEffect } from 'react';

type Theme = 'light' | 'dark';

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('darkmoor_theme') as Theme;
    return saved || 'dark';
  });

  useEffect(() => {
    localStorage.setItem('darkmoor_theme', theme);
    document.body.className = theme === 'dark' ? 'dark-theme' : 'light-theme';
    
    // Also set data-theme attribute for CSS
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return { theme, toggleTheme };
}