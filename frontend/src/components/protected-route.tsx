'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '../context/auth-context';
import { ReactNode, useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  fallbackUrl?: string;
}

const ProtectedRoute = ({
  children,
  fallbackUrl = '/signin'
}: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Store the attempted path for redirect after login
      sessionStorage.setItem('redirectAfterLogin', pathname);
      router.push(fallbackUrl);
    }
  }, [isAuthenticated, isLoading, router, fallbackUrl, pathname]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-background via-primary/5 to-background">
        <div className="relative">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary"></div>
          <div className="absolute inset-0 rounded-full bg-primary/20 blur-xl animate-pulse"></div>
        </div>
      </div>
    );
  }

  // If authenticated, render the protected content
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated and not loading, redirect will happen via useEffect
  // but we return null here to avoid rendering anything during redirect
  return null;
};

export default ProtectedRoute;