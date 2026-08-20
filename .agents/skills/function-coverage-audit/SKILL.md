---
name: function-coverage-audit
description: Callable inventory and function-by-function auditing skill for AI Attendance System.
---

# Function Coverage Audit Skill

## Purpose
Builds a complete inventory of every function and method in `app/` and classifies health state into GREEN, YELLOW, ORANGE, or RED categories.

## Classification Standard
- **GREEN**: Clean, tested, correctly handles inputs and outputs.
- **YELLOW**: Functional, but could be simplified or lacks direct unit test coverage.
- **ORANGE**: Maintainability or resource-handling concern.
- **RED**: Real defect, exception path, or data-integrity issue.
