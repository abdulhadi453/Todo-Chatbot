'use client';

import React from 'react';
import Link from 'next/link';
import Layout from '../src/components/layout/layout';
import { Button } from '../src/components/ui/button';
import { Card, CardContent } from '../src/components/ui/card';
import { Sparkles, Rocket, Zap, Globe, Shield, Heart } from 'lucide-react';

const LandingPage = () => {
  return (
    <Layout>
      <main className="min-h-screen flex flex-col">
        {/* Background elements */}
        <div className="absolute inset-0 overflow-hidden" aria-hidden="true">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent/10 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-primary/5 to-accent/5 rounded-full blur-3xl"></div>
        </div>

        <div className="relative z-10 flex-grow flex items-center justify-center">
          <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-16">
            <div className="text-center mb-10 sm:mb-16">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-sm font-medium mb-6 border border-primary/20">
                <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" />
                <span className="text-foreground">Experience the Next Generation</span>
              </div>

              <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-foreground mb-6">
                Transform Your Productivity
              </h1>

              <p className="text-lg sm:text-xl text-muted-foreground mx-auto mb-10">
                The most intuitive todo application designed to help you organize your daily tasks and boost productivity with cutting-edge features.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button asChild size="lg" className="px-8 py-4 text-base font-bold gap-2 h-12 rounded-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-primary/30">
                  <Link href="/signup">
                    Start Your Journey - It's Free
                    <Rocket className="h-4 w-4" aria-hidden="true" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="px-8 py-4 text-base font-bold h-12 rounded-full border-2 border-foreground/20 hover:border-primary/50 text-foreground hover:bg-primary/10 transition-all duration-300 transform hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-primary/30">
                  <Link href="/signin">Sign In</Link>
                </Button>
              </div>
            </div>

            <section className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 mb-12 sm:mb-16" aria-labelledby="features-heading">
              <h2 id="features-heading" className="sr-only">Key Features</h2>

              <Card className="border bg-card shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-primary/10" role="region" aria-labelledby="feature-1">
                <CardContent className="p-6 text-center space-y-4">
                  <div className="mx-auto w-12 h-12 rounded-full bg-gradient-to-r to-yellow-400 from-primary to-accent flex items-center justify-center transition-transform duration-300 hover:scale-110" aria-hidden="true">
                    <Zap className="h-6 w-6 text-primary-foreground" />
                  </div>
                  <h3 id="feature-1" className="text-xl font-bold text-foreground transition-colors duration-300">Lightning Fast</h3>
                  <p className="text-muted-foreground transition-colors duration-300">Experience blazing fast task management with our optimized interface.</p>
                </CardContent>
              </Card>

              <Card className="border bg-card shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-primary/10" role="region" aria-labelledby="feature-2">
                <CardContent className="p-6 text-center space-y-4">
                  <div className="mx-auto w-12 h-12 rounded-full bg-gradient-to-r to-violet-500 from-secondary to-muted flex items-center justify-center transition-transform duration-300 hover:scale-110" aria-hidden="true">
                    <Globe className="h-6 w-6 text-secondary-foreground" />
                  </div>
                  <h3 id="feature-2" className="text-xl font-bold text-foreground transition-colors duration-300">Cross Platform</h3>
                  <p className="text-muted-foreground transition-colors duration-300">Access your tasks from anywhere, on any device, anytime.</p>
                </CardContent>
              </Card>

              <Card className="border bg-card shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-primary/10" role="region" aria-labelledby="feature-3">
                <CardContent className="p-6 text-center space-y-4">
                  <div className="mx-auto w-12 h-12 rounded-full bg-gradient-to-r from-success to-emerald-500 flex items-center justify-center transition-transform duration-300 hover:scale-110" aria-hidden="true">
                    <Shield className="h-6 w-6 text-success-foreground" />
                  </div>
                  <h3 id="feature-3" className="text-xl font-bold text-foreground transition-colors duration-300">Secure & Private</h3>
                  <p className="text-muted-foreground transition-colors duration-300">Your data is protected with enterprise-grade security measures.</p>
                </CardContent>
              </Card>
            </section>

            <div className="max-w-3xl mx-auto text-center">
              <div className="inline-flex items-center gap-4 text-muted-foreground mb-4">
                <Heart className="h-5 w-5 text-destructive" aria-hidden="true" />
                <span>Made with love for productivity enthusiasts</span>
                <Heart className="h-5 w-5 text-destructive" aria-hidden="true" />
              </div>
              <p className="text-sm text-muted-foreground">
                Join thousands of users who have transformed their daily routine with our powerful yet simple todo app.
              </p>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
};

export default LandingPage;