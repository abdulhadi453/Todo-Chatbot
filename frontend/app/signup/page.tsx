'use client';

import React from 'react';
import Link from 'next/link';
import Layout from '../../src/components/layout/layout';
import SignupForm from '../../src/components/auth/signup-form';
import { Rocket } from 'lucide-react';

const SignupPage = () => {
  return (
    <Layout showHeader={true}>
      <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-background via-primary/5 to-background p-4">
        <div className="w-full max-w-fit">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-sm font-medium mb-6 border border-primary/20">
              <Rocket className="h-4 w-4 text-primary" aria-hidden="true" />
              <span className="text-foreground">Start Free</span>
            </div>
            <h1 className="text-3xl font-black bg-linear-to-r from-primary to-accent bg-clip-text">
              Create your account
            </h1>
          </div>

          <SignupForm />

          <div className="mt-8 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link href="/signin" className="font-medium text-primary hover:text-accent transition-colors">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SignupPage;