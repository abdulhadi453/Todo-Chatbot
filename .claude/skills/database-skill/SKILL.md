---
name: database-skill
description: Design robust database schemas, create tables, and manage migrations for scalable applications.
---

# Database Skill – Tables, Migrations & Schema Design

## Instructions

1. **Schema Planning**
   - Identify core entities and their attributes  
   - Define relationships between entities  
   - Normalize data to avoid duplication  
   - Decide primary and foreign keys  

2. **Table Creation**
   - Use clear and consistent naming conventions  
   - Choose correct data types for each field  
   - Apply constraints (NOT NULL, UNIQUE, DEFAULT)  
   - Add timestamps for auditing  

3. **Migrations**
   - Version every schema change  
   - Write reversible migrations (up/down)  
   - Keep migrations small and atomic  
   - Never edit old migrations in production  

4. **Relationships**
   - One-to-One  
   - One-to-Many  
   - Many-to-Many (via junction tables)  

## Best Practices
- Use `snake_case` for table and column names  
- Always index foreign keys  
- Avoid destructive changes on live databases  
- Document schema decisions  
- Test migrations in staging before production  
- Prefer additive changes over breaking ones  

## Example Structure

```sql
-- users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- posts table
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);