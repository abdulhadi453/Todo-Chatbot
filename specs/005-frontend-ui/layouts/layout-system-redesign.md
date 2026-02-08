# Layout System Redesign: Frontend UI Redesign

**Feature**: Frontend UI Enforcement & Visual Redesign
**Design Document**: Layout System Redesign
**Date**: 2026-01-23

## Container System

### Page Container
- **Width**: 100% of viewport width with max-width constraint
- **Max Width**: 1280px (7xl) for large screens
- **Centering**: Auto margins to center content
- **Padding**: 1rem (16px) on sides on mobile, 2rem (32px) on desktop
- **Position**: Static, not fixed

### Section Container
- **Width**: 100% of parent container
- **Padding**: 1.5rem (24px) vertical spacing between sections
- **Margin**: 0 horizontal
- **Background**: White or inherited from parent

## Grid System

### Responsive Breakpoints
- **Mobile**: 320px - 640px (max-width: 768px)
- **Tablet**: 640px - 1024px (min-width: 640px and max-width: 1024px)
- **Desktop**: 1024px+ (min-width: 1024px)

### Grid Columns
- **Mobile**: Single column layout (1fr)
- **Tablet**: Two column layout (repeat(2, 1fr))
- **Desktop**: Three to four column layout (repeat(3, 1fr) to repeat(4, 1fr))

### Gap Settings
- **Row Gap**: 1rem (16px) vertical spacing between grid items
- **Column Gap**: 1rem (16px) horizontal spacing between grid items
- **Responsive**: Increase to 1.5rem (24px) on desktop

## Card-Based Layout

### Todo Item Card
- **Width**: 100% of grid container
- **Height**: Auto, content-driven
- **Padding**: 1.5rem (24px) internal spacing
- **Border Radius**: 0.5rem (8px) rounded corners
- **Shadow**: Medium shadow for elevation
- **Spacing**: 1rem (16px) vertical gap between cards

### Card Content Structure
- **Top Row**: Checkbox and title with flex layout
- **Middle Row**: Description text
- **Bottom Row**: Meta information and action buttons
- **Spacing**: Consistent internal padding and margin

## Typography Hierarchy

### Vertical Rhythm
- **Line Height**: Maintain consistent line height ratios
- **Spacing**: Use spacing scale units for vertical margins
- **Hierarchy**: Clear differentiation between heading levels

### Responsive Scaling
- **Mobile**: Smaller font sizes and tighter spacing
- **Desktop**: Larger font sizes and more generous spacing
- **Scaling Factor**: 1.25 ratio between breakpoints

## Spacing System

### Internal Spacing
- **Component Padding**: 1rem (16px) for most components
- **Element Margins**: 0.5rem (8px) to 1rem (16px) between elements
- **Group Spacing**: 1.5rem (24px) between logical groups

### External Spacing
- **Section Margins**: 2rem (32px) between major sections
- **Page Margins**: 1rem (16px) on mobile, 2rem (32px) on desktop
- **Card Gaps**: 1rem (16px) between cards in lists

## Responsive Adjustments

### Mobile Layout
- **Single Column**: All content in single column
- **Touch Targets**: Minimum 44px for interactive elements
- **Font Sizes**: Slightly smaller for dense information

### Tablet Layout
- **Two Column**: Cards arranged in two columns where appropriate
- **Moderate Spacing**: Balanced spacing between mobile and desktop
- **Adjusted Typography**: Mid-range font sizes

### Desktop Layout
- **Multi-Column**: Up to four columns for cards
- **Generous Spacing**: More whitespace for better readability
- **Larger Typography**: Enhanced readability with bigger fonts

## Navigation & Header

### Header Layout
- **Position**: Sticky at top of viewport
- **Width**: 100% of viewport with centered content
- **Height**: 4rem (64px) minimum
- **Padding**: Side padding consistent with page container

### Footer Layout
- **Position**: Static at bottom of content
- **Width**: 100% of viewport with centered content
- **Height**: Auto, content-driven
- **Padding**: Same as header for consistency