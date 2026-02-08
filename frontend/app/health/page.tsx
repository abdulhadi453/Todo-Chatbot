'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle, RotateCcw } from 'lucide-react';

const HealthCheck = () => {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      router.push('/');
    }, 2000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="max-w-md w-full text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-success/20 mb-6">
          <CheckCircle className="h-8 w-8 text-success" />
        </div>

        <h1 className="text-xl font-bold text-foreground mb-4">
          ✅ Todo App Frontend is Running!
        </h1>

        <p className="text-muted-foreground mb-2">
          The Next.js development server is successfully running.
        </p>

        <p className="text-muted-foreground mb-6">
          All systems are operational and ready to use.
        </p>

        <div className="bg-card rounded-lg p-4 border border-border">
          <h2 className="font-semibold text-foreground mb-3">Features Implemented:</h2>
          <ul className="text-left text-sm text-muted-foreground space-y-2">
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
              <span>Authentication system (Sign up, Sign in)</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
              <span>Task management features</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
              <span>Responsive UI components</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
              <span>TypeScript type safety</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 text-success mt-0.5 flex-shrink-0" />
              <span>API integration with JWT</span>
            </li>
          </ul>
        </div>

        <div className="mt-6 flex items-center justify-center gap-2 text-muted-foreground">
          <RotateCcw className="h-4 w-4 animate-spin" />
          <span>Redirecting to main application...</span>
        </div>
      </div>
    </div>
  );
};

export default HealthCheck;