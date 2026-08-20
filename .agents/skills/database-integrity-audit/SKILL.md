---
name: database-integrity-audit
description: SQLite schema, foreign key, and transaction safety auditing skill for AI Attendance System.
---

# Database Integrity Audit Skill

## Purpose
Audits SQLite schema tables, foreign key constraints (`PRAGMA foreign_keys = ON;`), `UNIQUE(student_id, attendance_date)` protection, and transaction rollback contexts.

## Checklist
1. **Schema Consistency**: Verifies table definitions in `app/database/schema.py` match repository queries.
2. **Constraint Enforcement**: Confirms foreign key relationships and unique constraints.
3. **Transaction Contexts**: Verifies `get_db_connection()` handles commit and rollback cleanly.
