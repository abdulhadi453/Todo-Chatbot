import { cn } from '@/lib/utils';
import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'filled' | 'outline' | 'floating';
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className, variant = 'outline', ...props }, ref) => {
    const baseClasses = 'flex w-full rounded-lg border bg-background text-foreground text-base ring-offset-background file:border-0 file:bg-transparent file:text-base file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200';

    const variantClasses = {
      filled: 'border-input bg-input px-4 py-3',
      outline: 'border-input bg-background px-4 py-3',
      floating: 'border-input bg-background px-4 py-6 pt-8 focus-within:border-primary relative',
    };

    const errorClass = error ? 'border-destructive focus-visible:ring-destructive' : '';
    const successClass = props.value && !error ? 'border-success focus-visible:ring-success' : '';

    // Use the provided ID or let the browser generate a default one
    const inputId = props.id;
    const errorId = error ? `${inputId || 'input'}-error` : undefined;
    const helperId = helperText ? `${inputId || 'input'}-helper` : undefined;

    return (
      <div className="w-full relative">
        {label && variant !== 'floating' && (
          <label htmlFor={inputId} className={cn("block text-sm font-medium mb-2", error ? 'text-destructive' : 'text-foreground')}>
            {label}
          </label>
        )}

        {variant === 'floating' && label && (
          <label
            htmlFor={inputId}
            className={cn(
              "absolute left-4 top-3 text-muted-foreground text-sm pointer-events-none transition-all peer-focus:-top-2 peer-focus:left-4 peer-focus:text-xs peer-focus:text-primary peer-placeholder-shown:top-3 peer-placeholder-shown:text-sm peer-placeholder-shown:text-muted-foreground",
              error ? 'text-destructive' : 'text-muted-foreground'
            )}
          >
            {label}
          </label>
        )}

        <input
          ref={ref}
          id={inputId}
          className={cn(baseClasses, variantClasses[variant], errorClass, successClass, className)}
          aria-invalid={!!error}
          aria-describedby={errorId || helperId || undefined}
          {...props}
        />

        {helperText && !error && (
          <p id={helperId} className="mt-2 text-sm text-muted-foreground">{helperText}</p>
        )}
        {error && <p id={errorId} className="mt-2 text-sm text-destructive">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };