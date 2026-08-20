"""
Management Dashboard package for AI-Enabled Smart Attendance System.
Exposes dashboard metric calculation and activity summary services under RBAC.
"""

from app.dashboard.service import get_dashboard_metrics

__all__ = ["get_dashboard_metrics"]
