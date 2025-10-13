from django.urls import path
from .views import (
    ReportCreateView,
    ReportListView,
    ReportDetailView,
    ReportStatusUpdateView,
    MyReportsView,
    report_statistics,
    ReportWithActionsDetailView,
    ModerationActionCreateView,
    ModerationActionListView,
    ModeratorDashboardView,
    bulk_assign_reports,
    bulk_resolve_reports
)

app_name = 'moderation'

urlpatterns = [
    # Report submission
    path('reports/', ReportCreateView.as_view(), name='report-create'),
    
    # Report management (moderators only)
    path('reports/list/', ReportListView.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('reports/<int:pk>/update/', ReportStatusUpdateView.as_view(), name='report-update'),
    path('reports/<int:pk>/detailed/', ReportWithActionsDetailView.as_view(), name='report-detailed'),
    
    # Moderation actions
    path('reports/<int:report_id>/actions/', ModerationActionListView.as_view(), name='action-list'),
    path('reports/<int:report_id>/actions/create/', ModerationActionCreateView.as_view(), name='action-create'),
    
    # User's own reports
    path('my-reports/', MyReportsView.as_view(), name='my-reports'),
    
    # Moderator tools
    path('dashboard/', ModeratorDashboardView.as_view(), name='moderator-dashboard'),
    path('bulk-assign/', bulk_assign_reports, name='bulk-assign'),
    path('bulk-resolve/', bulk_resolve_reports, name='bulk-resolve'),
    
    # Statistics
    path('statistics/', report_statistics, name='report-statistics'),
]