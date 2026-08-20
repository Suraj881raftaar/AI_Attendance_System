---
name: python-architecture-review
description: Architecture and service-boundary auditing skill for AI Attendance System.
---

# Python Architecture Review Skill

## Purpose
Inspects architectural layer decoupling across UI, application service layer, AI engine, repository layer, and SQLite database persistence.

## Checklist
1. **Layer Separation**: Verifies UI components do not query SQLite directly; all requests flow through service modules.
2. **Provider Abstraction**: Ensures frame sources implement the `FrameProvider` base interface.
3. **Configuration Isolation**: Verifies central configuration (`app/config.py`) handles runtime vs PyInstaller frozen paths cleanly.
