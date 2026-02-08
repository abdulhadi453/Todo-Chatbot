'use client';

import React from 'react';
import Link from 'next/link';
import Layout from '../../src/components/layout/layout';
import SigninForm from '../../src/components/auth/signin-form';
import { Sparkles } from 'lucide-react';

const SigninPage = () => {
  return (
    <Layout showHeader={true}>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-primary/5 to-background p-4">
        <div className="w-full max-w-fit">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-sm font-medium mb-6 border border-primary/20" aria-label="Application tagline">
              <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" />
              <span className="text-foreground">Welcome Back</span>
            </div>

            <h1 className="text-3xl font-black bg-gradient-to-r from-primary to-accent bg-clip-text" role="heading" aria-level={1}>
              Sign in to your account
            </h1>
          </div>

          <SigninForm />

          <div className="mt-8 text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="font-medium text-primary hover:text-accent">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SigninPage;
