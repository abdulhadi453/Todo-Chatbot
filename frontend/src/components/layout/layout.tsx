import React from 'react';
import Header from './header';

interface LayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
}

const Layout = ({ children, showHeader = true }: LayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Header */}
      {showHeader && <Header />}

      {/* 
        MAIN CONTENT
        - Do NOT wrap children in container here
        - Auth pages manage their own width (max-w-md)
        - Dashboard pages already handle layout internally
      */}
      <main className="flex-1 flex flex-col">
        {children}
      </main>

      {/* Footer (UNCHANGED) */}
      <footer className="py-6 sm:py-8 border-t border-border bg-muted">
        <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Todo App. All rights reserved.
            </p>

            <div className="flex gap-6 mt-4 md:mt-0">
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded"
              >
                Terms
              </a>
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded"
              >
                Privacy
              </a>
              <a
                href="#"
                className="text-sm text-muted-foreground hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded"
              >
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;