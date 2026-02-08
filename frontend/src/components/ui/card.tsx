import { cn } from '@/lib/utils';
import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const Card = ({ children, className, ...props }: CardProps) => {
  const cardClasses = cn(
    'rounded-xl border bg-card text-card-foreground shadow-sm transition-all duration-200',
    className
  );

  return (
    <div
      className={cardClasses}
      {...props}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardHeader = ({ children, className, ...props }: CardHeaderProps) => {
  return (
    <div className={cn("flex flex-col space-y-2 p-6 pb-4", className)} {...props}>
      {children}
    </div>
  );
};

interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

const CardTitle = ({ children, className, ...props }: CardTitleProps) => {
  return (
    <h3 className={cn("font-bold text-xl leading-tight text-foreground", className)} {...props}>
      {children}
    </h3>
  );
};

interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

const CardDescription = ({ children, className, ...props }: CardDescriptionProps) => {
  return (
    <p className={cn("text-sm text-muted-foreground", className)} {...props}>
      {children}
    </p>
  );
};

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardContent = ({ children, className, ...props }: CardContentProps) => {
  return (
    <div className={cn("p-6 pt-2", className)} {...props}>
      {children}
    </div>
  );
};

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardFooter = ({ children, className, ...props }: CardFooterProps) => {
  return (
    <div className={cn("flex items-center p-6 pt-2", className)} {...props}>
      {children}
    </div>
  );
};

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };