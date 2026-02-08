---
id: 2
title: "Update Phase II to Phase III AI Todo Chatbot"
stage: "constitution"
date: "2026-02-06"
surface: "agent"
model: "Claude Sonnet 4.5"
feature: "none"
branch: "master"
user: "user"
command: "sp.constitution Update Phase II Constitution → Phase III AI Todo Chatbot"
labels: ["constitution", "governance", "spec-driven-development", "ai-integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ".specify/memory/constitution.md"
tests:
  - "constitution validation"
---

## Prompt

Update Phase II Constitution → Phase III AI Todo Chatbot

You are tasked with updating an existing `sp.constitution` for a project that was previously Phase II (Full-Stack Web App). The new version is **Phase III**, which introduces an AI-powered Todo Chatbot with OpenAI Agents SDK and MCP integration.

## Instructions

1. **Use Phase II Constitution as Base**
   - Keep all core principles, development workflow, quality standards, and governance structure.
   - Update or extend sections as needed to support AI functionality.

2. **Update Versioning**
   - Increment version from `1.0.0` → `2.0.0`.
   - Update `Ratified` and `Last Amended` dates to today.

3. **Core Principles Enhancements**
   - Add AI-first development principle:
     - All new AI features must follow **Spec-Driven Development** and **Agentic Dev Stack workflow**.
     - All AI behavior must be stateless on the server and use MCP tools for task operations.
     - AI agents are authorized through the existing Better Auth system.
   - Maintain backward compatibility for Phase II Todo features.
   - Ensure separation of AI logic from existing backend services, using **MCP server** as the tool layer.

4. **Technology Stack Updates**
   - **Frontend:** OpenAI ChatKit (integrated with Next.js)
   - **Backend:** Python FastAPI + OpenAI Agents SDK
   - **MCP Server:** Official MCP SDK exposing task tools
   - **Database:** Neon Serverless PostgreSQL (add tables: `Conversations`, `Messages` for chat)
   - **ORM:** SQLModel
   - **Authentication:** Better Auth with JWT

5. **Architecture & API**
   - Include stateless chat endpoint:
     - `POST /api/{user_id}/chat`
     - Request: `conversation_id` (optional), `message` (required)
     - Response: `conversation_id`, `response`, `tool_calls`
   - Specify MCP tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task` with parameters and expected outputs.
   - Document agent behavior for mapping natural language commands to MCP tools.

6. **Development Workflow & Quality Standards**
   - All AI features generated via Claude Code (no manual coding).
   - Follow Phase II testing, logging, and security standards.
   - Ensure conversation state persistence in the database but server remains stateless.
   - Add AI-specific error handling and confirmation messaging.

7. **Database Models**
   - Update models for AI features:
     - `Task` (existing)
     - `Conversation` (user_id, id, created_at, updated_at)
     - `Message` (user_id, id, conversation_id, role, content, created_at)
   - Ensure relationships maintain multi-user security and integrity.

8. **Deliverables**
   - Fully working AI Todo Chatbot integrated with existing Phase II app.
   - Updated constitution file reflecting Phase III requirements.
   - Database migration scripts for new tables.
   - README update to reflect Phase III setup and usage.

9. **Formatting**
   - Keep Markdown structure consistent with Phase II.
   - Use clear section headings: Core Principles, Technology Stack Requirements, Development Workflow & Quality Standards, Governance, etc.
   - Add AI-specific sub-sections where necessary.

10. **Output**
    - Return the updated `sp.constitution` in Markdown.
    - Include updated versioning, ratification date, and all Phase III enhancements.

## Response

Updated the project constitution at `.specify/memory/constitution.md` to reflect the Phase III AI Todo Chatbot requirements. The updated constitution includes:

1. All original Phase II principles plus four new AI-specific principles (VII-X)
2. Technology stack requirements expanded to include OpenAI ChatKit, OpenAI Agents SDK, and MCP Server
3. New API contract requirement for the stateless chat endpoint at `POST /api/{user_id}/chat`
4. Enhanced security requirements for AI agents to inherit user permissions
5. Detailed MCP tool specifications (`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`)
6. Database requirements for `Conversations` and `Messages` tables
7. Updated authentication flow to include AI agent authorization
8. AI-specific development and testing requirements
9. Version incremented from 1.0.0 to 2.0.0 with updated ratification date

The constitution maintains backward compatibility with Phase II features while adding comprehensive AI integration requirements.

## Outcome

- ✅ Impact: Successfully updated the project constitution to reflect Phase III AI Todo Chatbot requirements
- 🧪 Tests: constitution validation
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: None needed - constitution update complete
- 🧠 Reflection: The updated constitution properly balances maintaining Phase II functionality with new AI requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A