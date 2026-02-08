'use client';

import Link from 'next/link';
import { useAuth } from '../../context/auth-context';
import { Button } from '../ui/button';
import { useTheme } from '../../context/theme-context';
import { MoonIcon, SunIcon } from 'lucide-react';

const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-background/90 backdrop-blur border-b border-border" role="banner">
      <div className="container flex h-16 items-center justify-between max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center space-x-3" aria-label="Todo App Home">
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text">Todo App</span>
          </Link>

          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium" aria-label="Main navigation">
            <Link
              href="/dashboard"
              className="transition-colors hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary rounded-lg px-3 py-2"
            >
              Dashboard
            </Link>
            <Link
              href="/chat"
              className="transition-colors hover:text-primary focus:outline-none focus:ring-2 focus:ring-primary rounded-lg px-3 py-2"
            >
              AI Chat
            </Link>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          {/* Theme toggle button */}
          <Button
            variant="outline"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            className="focus:outline-none focus:ring-2 focus:ring-primary rounded-lg"
          >
            {theme === 'dark' ? (
              <SunIcon className="h-5 w-5" aria-hidden="true" />
            ) : (
              <MoonIcon className="h-5 w-5" aria-hidden="true" />
            )}
          </Button>

          {isAuthenticated ? (
            <>
              <span className="hidden md:inline-flex items-center text-sm font-medium bg-muted px-3 py-1.5 rounded-full" aria-live="polite">
                Welcome, {user?.name || user?.email}
              </span>
              <Button
                variant="outline"
                onClick={handleLogout}
                className="focus:outline-none focus:ring-2 focus:ring-primary rounded-lg"
                aria-label="Logout"
              >
                Logout
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="outline"
                asChild
                className="focus:outline-none focus:ring-2 focus:ring-primary rounded-lg"
              >
                <Link href="/signin">Sign In</Link>
              </Button>
              <Button
                asChild
                className="focus:outline-none focus:ring-2 focus:ring-primary rounded-lg bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground"
              >
                <Link href="/signup">Sign Up</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;