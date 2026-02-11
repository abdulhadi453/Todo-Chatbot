import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Utility function to generate gradient classes for consistent design
 */
export function getGradientClass(color: 'primary' | 'secondary' | 'accent' | 'success' | 'warning' | 'destructive') {
  switch (color) {
    case 'primary':
      return 'from-primary to-accent';
    case 'secondary':
      return 'from-secondary to-muted';
    case 'accent':
      return 'from-accent to-primary';
    case 'success':
      return 'from-success to-emerald-500';
    case 'warning':
      return 'from-warning to-orange-500';
    case 'destructive':
      return 'from-destructive to-red-600';
    default:
      return 'from-primary to-accent';
  }
}

/**
 * Utility function to generate consistent shadow classes
 */
export function getShadowClass(level: 'sm' | 'md' | 'lg' | 'xl' | '2xl') {
  switch (level) {
    case 'sm':
      return 'shadow-md';
    case 'md':
      return 'shadow-lg';
    case 'lg':
      return 'shadow-xl';
    case 'xl':
      return 'shadow-2xl';
    case '2xl':
      return 'shadow-[0_25px_50px_-12px_rgba(0,0,0,0.25)]';
    default:
      return 'shadow-md';
  }
}