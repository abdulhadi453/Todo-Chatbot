---
id: 1
title: "Update Constitution"
stage: "constitution"
date_iso: "2026-01-14"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "master"
user: "user"
command: "sp.constitution"
labels:
  - "constitution"
  - "governance"
  - "spec-driven-development"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - ".specify/memory/constitution.md"
tests_yaml:
  - "constitution validation"
outcome: "Successfully updated the project constitution to reflect Phase II Todo Full-Stack Web Application requirements"
evaluation: "Constitution properly reflects all required principles and standards from user input"
---

# Prompt History Record: Update Constitution

## Original Prompt

Phase II – Todo Full-Stack Web Application

Core principles:
- Spec-Driven Development first (no implementation without an approved spec)
- Zero manual coding; all source code generated via Claude Code
- Backward compatibility with Phase I domain behavior
- Clear separation of frontend, backend, and data layers
- Secure, multi-user design by default

Key standards:
- Every feature must have:
  - A Markdown Spec
  - A Plan
  - Task breakdown
  - Claude-generated implementation
- REST API must be deterministic and versionable
- Frontend and backend must communicate only via defined HTTP contracts
- Authentication and authorization must be enforced for all user data access

Architecture standards:
- Frontend: Next.js 16+ (App Router)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (JWT-based)
- All Todo operations must be user-scoped

Security standards:
- All API requests must require JWT authentication
- Backend must:
  - Extract `Authorization: Bearer <token>`
  - Verify token signature using shared secret
  - Decode user identity from token
  - Enforce that `{user_id}` in route matches token user
- No cross-user data access is allowed
- Unauthorized or mismatched access must return proper HTTP errors

API contract (must be preserved):
- GET    /api/{user_id}/tasks
- POST   /api/{user_id}/tasks
- GET    /api/{user_id}/tasks/{id}
- PUT    /api/{user_id}/tasks/{id}
- DELETE /api/{user_id}/tasks/{id}
- PATCH  /api/{user_id}/tasks/{id}/complete

Todo domain standards:
- Each task includes:
  - Unique ID
  - Description
  - Completion status
  - Owner (user_id)
- Core operations:
  - Add, update, delete, list, toggle completion
- Behavior must match Phase I semantics

Constraints:
- No console interface
- No in-memory storage
- No bypassing authentication
- No manual code edits
- Specs must be explicit and unambiguous
- English-only specifications

Success criteria:
- Fully functional multi-user web app
- Responsive Next.js frontend
- Secure REST API with JWT verification
- All Todo operations scoped per user
- Data persists in Neon PostgreSQL
- All code generated solely from specs via Claude Code
- Phase II passes all functional and security requirements without manual fixes

## Response Summary

Updated the project constitution at `.specify/memory/constitution.md` to reflect the Phase II Todo Full-Stack Web Application requirements. The new constitution includes:

1. Six core principles covering Spec-Driven Development, zero manual coding, backward compatibility, separation of concerns, secure multi-user design, and RESTful API contracts
2. Technology stack requirements for frontend (Next.js), backend (FastAPI), database (Neon PostgreSQL), and authentication (Better Auth)
3. Detailed authentication flow requirements
4. Development workflow and quality standards
5. Governance and amendment procedures

The constitution includes a Sync Impact Report at the top and follows all formatting requirements with proper versioning and dates.

## Files Modified

- `.specify/memory/constitution.md`: Updated to include all Phase II requirements and principles