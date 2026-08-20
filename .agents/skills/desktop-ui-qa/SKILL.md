---
name: desktop-ui-qa
description: CustomTkinter GUI lifecycle, callback, and widget auditing skill for AI Attendance System.
---

# Desktop UI QA Skill

## Purpose
Inspects all CustomTkinter frames, windows, widgets, buttons, callbacks, modal dialogs, and font lifecycle bindings.

## Checklist
1. **Window & Font Lifecycle**: Checks that `CTkFont` instances are not instantiated before default root window initialization or after window destruction.
2. **Callback Signatures**: Verifies all button and event callbacks match required positional/keyword argument signatures.
3. **Widget Destruction Safety**: Verifies `destroy()` and `self.status_label.configure()` calls handle closed window states safely without raising `TclError`.
4. **Navigation & Refresh**: Checks tab switching, confirmation dialogs, empty state placeholders, and Matplotlib canvas re-rendering.
