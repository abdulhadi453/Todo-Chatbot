import { cn } from '@/lib/utils';
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'destructive' | 'ghost' | 'link' | 'neon';
  size?: 'sm' | 'md' | 'lg' | 'icon';
  isLoading?: boolean;
  children: React.ReactNode;
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', isLoading, children, className, asChild, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center whitespace-nowrap rounded-full font-bold transition-all duration-300 ease-out border-2 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-primary/30 disabled:pointer-events-none disabled:opacity-50 cursor-pointer shadow-lg hover:shadow-2xl active:scale-[0.97] hover:transform hover:-translate-y-0.5';

    const variantClasses = {
      primary: 'bg-gradient-to-r from-primary to-accent text-primary-foreground border-transparent hover:from-primary/90 hover:to-accent/90',
      secondary: 'bg-gradient-to-r from-secondary to-muted text-secondary-foreground border-transparent hover:from-secondary/90 hover:to-muted/90',
      outline: 'bg-transparent text-foreground border-foreground hover:bg-gradient-to-r hover:from-foreground hover:to-foreground/80 hover:text-background',
      destructive: 'bg-gradient-to-r from-destructive to-destructive/80 text-destructive-foreground border-transparent hover:from-destructive/90 hover:to-destructive/70',
      ghost: 'bg-transparent text-foreground hover:bg-gradient-to-r hover:from-primary/10 hover:to-accent/10 focus-visible:ring-primary/30',
      link: 'bg-transparent text-primary underline-offset-4 hover:underline hover:text-accent focus-visible:ring-primary/30',
      neon: 'bg-background text-foreground border-primary shadow-[0_0_15px_rgba(221,119,255,0.4)] hover:shadow-[0_0_30px_rgba(221,119,255,0.7)] hover:from-primary/10 hover:to-accent/10'
    };

    const sizeClasses = {
      sm: 'h-10 px-4 py-2 text-sm',
      md: 'h-12 px-6 py-3 text-base',
      lg: 'h-14 px-8 py-4 text-lg',
      icon: 'h-10 w-10',
    };

    const classes = cn(baseClasses, variantClasses[variant], sizeClasses[size], className);

    if (asChild && React.isValidElement(children)) {
      const child = children as React.ReactElement<React.AllHTMLAttributes<HTMLElement>>;
      return React.cloneElement(child, {
        className: cn(classes, child.props.className),
        disabled: isLoading || props.disabled,
        ...props
      });
    }

    return (
      <button
        ref={ref}
        className={classes}
        disabled={isLoading || props.disabled}
        aria-disabled={isLoading || props.disabled}
        {...props}
      >
        {isLoading ? (
          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden="true"></span>
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };