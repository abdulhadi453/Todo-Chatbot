---
name: auth-skill
description: Implement secure authentication systems with signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Registration (Signup)**

   - Validate user input (email, password, username)
   - Hash passwords before storing
   - Prevent duplicate accounts
   - Return clear success/error responses

2. **User Login (Signin)**

   - Verify credentials securely
   - Compare hashed passwords
   - Issue access and refresh tokens
   - Handle invalid attempts safely

3. **Security Layer**

   - Use strong hashing (bcrypt/argon2)
   - Never store plain-text passwords
   - Apply rate limiting
   - Sanitize all inputs

4. **JWT Token Flow**

   - Generate signed JWT tokens
   - Set expiration times
   - Verify tokens on protected routes
   - Support token refresh

5. **Better Auth Integration**
   - Configure Better Auth provider
   - Sync users with your database
   - Handle OAuth callbacks
   - Map external profiles to internal users

## Best Practices

- Enforce strong password rules
- Use HTTPS for all auth routes
- Store secrets in environment variables
- Separate auth logic into services
- Log auth events without sensitive data
- Always return generic auth errors

## Example Structure

```ts
// signup.ts
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

export async function signup(req, res) {
  const { email, password } = req.body;

  const hash = await bcrypt.hash(password, 12);
  const user = await db.user.create({ email, password: hash });

  const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET, {
    expiresIn: "1h",
  });

  res.json({ user: { id: user.id, email: user.email }, token });
}
```
