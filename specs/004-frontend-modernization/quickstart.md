# Quickstart Guide: Frontend UI/UX Modernization

## Overview
This guide provides essential information to quickly understand and contribute to the frontend modernization effort. The goal is to transform the existing Next.js frontend into a modern, responsive, and visually appealing application while preserving all functionality.

## Prerequisites

### System Requirements
- Node.js 18.x or higher
- npm or yarn package manager
- Git version control
- Modern web browser for testing

### Project Setup
```bash
# Clone the repository
git clone <repository-url>

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Development Workflow

### 1. Understanding the Structure
```
frontend/
├── app/                 # Next.js App Router pages
│   ├── dashboard/
│   ├── signin/
│   ├── signup/
│   └── globals.css      # Global styles and theme
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── layout/
│   │   ├── task/
│   │   ├── ui/          # Base UI components
│   │   └── services/    # API clients
│   ├── context/         # React context providers
│   └── types/           # TypeScript definitions
```

### 2. Key Technologies
- **Next.js 16+**: App Router for routing
- **React 19.2.3**: Component library
- **Tailwind CSS**: Styling and utility classes
- **TypeScript**: Type safety
- **Lucide React**: Icon library

### 3. Making UI Changes
1. **Global Styles**: Modify `app/globals.css` for theme and design system
2. **Base Components**: Update components in `src/components/ui/`
3. **Feature Components**: Enhance components in `src/components/task/`
4. **Pages**: Improve page layouts in `app/` directory

## Design System

### Color Palette
```css
/* In globals.css */
--color-primary: 0 122 255;     /* blue-500 */
--color-secondary: 240 240 240; /* gray-100 */
--color-accent: 144 19 254;     /* violet-600 */
--color-destructive: 239 68 68; /* red-500 */
--color-success: 34 197 94;     /* green-500 */
--color-warning: 245 158 11;    /* amber-500 */
```

### Spacing Scale
- `--spacing-xs`: 0.5rem (8px)
- `--spacing-sm`: 0.75rem (12px)
- `--spacing-md`: 1rem (16px)
- `--spacing-lg`: 1.5rem (24px)
- `--spacing-xl`: 2rem (32px)
- `--spacing-2xl`: 3rem (48px)

### Typography Scale
- `text-xs`: 0.75rem (12px)
- `text-sm`: 0.875rem (14px)
- `text-base`: 1rem (16px)
- `text-lg`: 1.125rem (18px)
- `text-xl`: 1.25rem (20px)
- `text-2xl`: 1.5rem (24px)

## Component Development

### Creating New UI Components
1. Add to `src/components/ui/` directory
2. Follow the existing component pattern with variants and props
3. Export from the component file
4. Import and use in other components

### Updating Existing Components
1. Locate the component in the appropriate directory
2. Maintain the existing API contract
3. Add new variants or properties as needed
4. Ensure backward compatibility

## Responsive Design

### Breakpoints
- `sm`: 640px and above
- `md`: 768px and above
- `lg`: 1024px and above
- `xl`: 1280px and above
- `2xl`: 1536px and above

### Responsive Classes
Use Tailwind's responsive prefixes:
```jsx
<div className="text-base md:text-lg lg:text-xl">
  Responsive text
</div>
```

## Accessibility Guidelines

### Semantic HTML
- Use proper heading hierarchy (h1, h2, h3...)
- Use semantic elements (nav, main, article, section)
- Include alt text for images

### ARIA Attributes
- Add `aria-label` for icon-only buttons
- Use `role` attributes when necessary
- Include `aria-describedby` for additional context

### Keyboard Navigation
- Ensure all interactive elements are keyboard accessible
- Add focus states for keyboard users
- Test with `Tab` navigation

## Testing and Validation

### Visual Testing
1. Test on different screen sizes
2. Verify consistent spacing and alignment
3. Check color contrast ratios
4. Validate responsive behavior

### Browser Testing
- Chrome, Firefox, Safari, Edge
- Mobile browsers (iOS Safari, Chrome Mobile)
- Tablet devices

### Accessibility Testing
- Use browser developer tools
- Run automated tools like axe-core
- Test with screen readers
- Verify keyboard navigation

## Common Tasks

### Updating the Theme
1. Modify color values in `app/globals.css`
2. Update both light and dark theme values
3. Test contrast ratios
4. Verify component appearances

### Adding New Icons
1. Install from Lucide React: `npm install lucide-react`
2. Import the specific icon: `import { IconName } from 'lucide-react'`
3. Use in components: `<IconName />`

### Creating New Pages
1. Add to `app/` directory
2. Use Next.js App Router conventions
3. Include proper layout and metadata
4. Follow design system guidelines

## Troubleshooting

### Component Not Rendering
- Check import statements
- Verify component exports
- Look for TypeScript errors

### Styles Not Applying
- Check Tailwind class names
- Verify Tailwind is properly configured
- Check for conflicting styles

### Responsive Issues
- Verify breakpoint usage
- Check for fixed widths that prevent scaling
- Test on actual devices when possible