# Quickstart Guide: Next.js Frontend Web Application

**Feature**: Next.js Frontend Web Application
**Date**: 2026-01-15
**Author**: Claude Sonnet 4.5

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Access to the backend API (FastAPI server running)

## Setup Instructions

### 1. Clone and Initialize
```bash
# Navigate to the project directory
cd /path/to/project

# Create frontend directory
mkdir frontend
cd frontend
```

### 2. Initialize Next.js Project
```bash
# Create Next.js app with TypeScript
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Install additional dependencies
npm install @types/node
```

### 3. Install Authentication Dependencies
```bash
# Install Better Auth and related packages
npm install better-auth @better-auth/react
```

### 4. Install API Client Dependencies
```bash
# Install axios for API calls
npm install axios
# Install types if needed
npm install @types/axios
```

### 5. Environment Configuration
Create a `.env.local` file in the frontend root:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret-from-backend
```

### 6. Run Development Server
```bash
# Start the development server
npm run dev

# The app will be available at http://localhost:3000
```

## Key Directories and Files

- `src/app/` - Next.js App Router pages
- `src/lib/` - Utility functions and API client
- `src/components/` - Reusable UI components
- `src/hooks/` - Custom React hooks
- `src/types/` - TypeScript type definitions

## Common Commands

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run production build locally
npm start

# Run linting
npm run lint

# Run tests (when implemented)
npm run test
```

## API Integration

The frontend communicates with the backend API located at the URL specified in `NEXT_PUBLIC_API_BASE_URL`. All authenticated requests will automatically include the JWT token in the Authorization header.