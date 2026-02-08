---
name: frontend-skill
description: Build responsive pages, reusable components, clean layouts, and modern styling. Use for frontend development tasks.
---

# Frontend Skill – Pages, Components & Layout

## Instructions

1. **Page Structure**
   - Use semantic HTML (`header`, `main`, `section`, `footer`)
   - Maintain clear content hierarchy
   - Add accessible landmarks

2. **Components**
   - Create reusable UI blocks (cards, buttons, forms, navbars)
   - Keep single responsibility per component
   - Support props-based customization

3. **Layout System**
   - Use Flexbox and Grid
   - Follow mobile-first breakpoints
   - Apply a consistent spacing scale

4. **Styling**
   - Use utility-first or modular CSS
   - Define design tokens (colors, spacing, fonts)
   - Support Light/Dark themes

## Best Practices
- Build mobile-first, enhance for desktop
- Keep components small and reusable
- Maintain consistent spacing and typography
- Avoid inline styles
- Ensure accessibility (labels, contrast, focus states)

## Example Structure
```html
<main class="container">
  <header class="page-header">
    <h1 class="title">Dashboard</h1>
  </header>

  <section class="grid">
    <article class="card">
      <h2 class="card-title">Stats</h2>
      <p class="card-body">Content here</p>
      <button class="btn-primary">View</button>
    </article>

    <article class="card">
      <h2 class="card-title">Activity</h2>
      <p class="card-body">Content here</p>
      <button class="btn-secondary">Open</button>
    </article>
  </section>
</main>