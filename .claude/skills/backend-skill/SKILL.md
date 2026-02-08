---
name: backend-skill
description: Generate API routes, handle requests/responses, and connect to databases. Use for backend service development.
---

# Backend Skill

## Instructions

1. **Routing**
   - Define RESTful endpoints (GET, POST, PUT, DELETE)
   - Use clear, resource-based paths
   - Group routes by feature/module

2. **Request & Response Handling**
   - Validate incoming data (params, body, headers)
   - Return consistent JSON responses
   - Handle errors with proper HTTP status codes

3. **Database Integration**
   - Connect to a database (SQL or NoSQL)
   - Use models/schemas for data structure
   - Perform CRUD operations safely

## Best Practices
- Use async/await for I/O operations  
- Centralize error handling  
- Keep controllers thin and services reusable  
- Never expose sensitive data in responses  
- Use environment variables for secrets  

## Example Structure
```js
// routes/user.routes.js
import express from "express";
import { createUser, getUser } from "../controllers/user.controller.js";

const router = express.Router();

router.post("/users", createUser);
router.get("/users/:id", getUser);

export default router;