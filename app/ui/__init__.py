"""
User Interface package for AI-Enabled Smart Attendance System.
Exposes CustomTkinter view components for Login, Student Management, Face Registration, and AI Attendance Engine.
"""

from app.ui.login import LoginWindow
from app.ui.students import StudentManagementFrame
from app.ui.registration_view import FaceRegistrationDialog
from app.ui.attendance import AttendanceViewFrame
from app.ui.dashboard import DashboardViewFrame
from app.ui.reports import ReportsViewFrame
from app.ui.analytics import AnalyticsViewFrame
from app.ui.main_window import MainWindow
from app.ui.components import ConfirmationDialog, EmptyStateWidget

__all__ = [
    "LoginWindow",
    "StudentManagementFrame",
    "FaceRegistrationDialog",
    "AttendanceViewFrame",
    "DashboardViewFrame",
    "ReportsViewFrame",
    "AnalyticsViewFrame",
    "MainWindow",
    "ConfirmationDialog",
    "EmptyStateWidget",
]
