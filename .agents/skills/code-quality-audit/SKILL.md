---
name: code-quality-audit
description: Deep Python code quality and static inspection skill for AI Attendance System.
---

# Code Quality Audit Skill

## Purpose
Performs thorough static code quality analysis across all Python modules in `app/`, `tests/`, and root scripts.

## Scope of Inspection
1. **Unused & Dead Code**: Identifies unused imports, dead functions, unreferenced classes, and unreachable branches.
2. **Resource Management**: Checks OpenCV camera release, Tkinter window destruction, SQLite connection closing, and Matplotlib canvas cleanup.
3. **Exception Safety**: Audits `except Exception` blocks, swallowed exceptions, and missing logging.
4. **Code Structure**: Evaluates function length, class responsibility, nesting depth, and parameter naming consistency.

## Rules
- Do NOT automatically edit production code.
- Report all findings with file links and line numbers.
