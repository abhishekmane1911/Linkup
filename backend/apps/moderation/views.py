from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Report, ModerationAction
from .serializers import (
    ReportCreateSerializer,
    ReportListSerializer,
    ReportDetailSerializer,
    ReportStatusUpdateSerializer,
    ModerationActionSerializer,
    ModerationActionCreateSerializer,
    ReportWithActionsSerializer
)

User = get_user_model()


class ReportPagination(PageNumberPagination):
    """Custom pagination for reports."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReportCreateView(generics.CreateAPIView):
    """
    Create a new report for content or users.
    """
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Save the report with the current user as reporter."""
        # Check if user has already reported this content
        content_type = serializer.validated_data['content_type']
        object_id = serializer.validated_data['object_id']
        
        existing_report = Report.objects.filter(
            reporter=self.request.user,
            content_type=content_type,
            object_id=object_id
        ).first()
        
        if existing_report:
            return Response(
                {'error': 'You have already reported this content.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(reporter=self.request.user)


class ReportListView(generics.ListAPIView):
    """
    List reports with filtering and search capabilities.
    Available to moderators and staff only.
    """
    serializer_class = ReportListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReportPagination
    
    def get_queryset(self):
        """Get reports based on user permissions and filters."""
        user = self.request.user
        
        # Only allow staff/moderators to view reports
        if not (user.is_staff or user.is_superuser):
            return Report.objects.none()
        
        queryset = Report.objects.select_related(
            'reporter', 'assigned_moderator', 'resolved_by', 'content_type'
        )
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by report type
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        # Filter by assigned moderator
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to == 'me':
            queryset = queryset.filter(assigned_moderator=user)
        elif assigned_to == 'unassigned':
            queryset = queryset.filter(assigned_moderator__isnull=True)
        
        # Search by reporter username
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(reporter__username__icontains=search) |
                Q(reporter__first_name__icontains=search) |
                Q(reporter__last_name__icontains=search)
            )
        
        return queryset


class ReportDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed information about a specific report.
    Available to moderators and staff only.
    """
    serializer_class = ReportDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reports based on user permissions."""
        user = self.request.user
        
        # Only allow staff/moderators to view reports
        if not (user.is_staff or user.is_superuser):
            return Report.objects.none()
        
        return Report.objects.select_related(
            'reporter', 'assigned_moderator', 'resolved_by', 'content_type'
        )


class ReportStatusUpdateView(generics.UpdateAPIView):
    """
    Update report status and resolution notes.
    Available to moderators and staff only.
    """
    serializer_class = ReportStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reports based on user permissions."""
        user = self.request.user
        
        # Only allow staff/moderators to update reports
        if not (user.is_staff or user.is_superuser):
            return Report.objects.none()
        
        return Report.objects.all()


class MyReportsView(generics.ListAPIView):
    """
    List reports submitted by the current user.
    """
    serializer_class = ReportListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReportPagination
    
    def get_queryset(self):
        """Get reports submitted by the current user."""
        return Report.objects.filter(
            reporter=self.request.user
        ).select_related(
            'assigned_moderator', 'resolved_by', 'content_type'
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def report_statistics(request):
    """
    Get report statistics for moderators.
    """
    user = request.user
    
    # Only allow staff/moderators to view statistics
    if not (user.is_staff or user.is_superuser):
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Calculate statistics
    total_reports = Report.objects.count()
    pending_reports = Report.objects.filter(status='pending').count()
    under_review_reports = Report.objects.filter(status='under_review').count()
    resolved_reports = Report.objects.filter(status='resolved').count()
    dismissed_reports = Report.objects.filter(status='dismissed').count()
    escalated_reports = Report.objects.filter(status='escalated').count()
    
    # Reports by type
    report_types = {}
    for report_type, _ in Report.REPORT_TYPES:
        count = Report.objects.filter(report_type=report_type).count()
        report_types[report_type] = count
    
    # My assigned reports (if moderator)
    my_assigned = Report.objects.filter(assigned_moderator=user).count()
    
    statistics = {
        'total_reports': total_reports,
        'status_breakdown': {
            'pending': pending_reports,
            'under_review': under_review_reports,
            'resolved': resolved_reports,
            'dismissed': dismissed_reports,
            'escalated': escalated_reports,
        },
        'report_types': report_types,
        'my_assigned_reports': my_assigned,
    }
    
    return Response(statistics)


class ReportWithActionsDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed report information including moderation actions.
    Available to moderators and staff only.
    """
    serializer_class = ReportWithActionsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get reports based on user permissions."""
        user = self.request.user
        
        # Only allow staff/moderators to view reports
        if not (user.is_staff or user.is_superuser):
            return Report.objects.none()
        
        return Report.objects.select_related(
            'reporter', 'assigned_moderator', 'resolved_by', 'content_type'
        ).prefetch_related(
            'moderation_actions__moderator'
        )


class ModerationActionCreateView(generics.CreateAPIView):
    """
    Create a new moderation action for a report.
    Available to moderators and staff only.
    """
    serializer_class = ModerationActionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        """Add report to serializer context."""
        context = super().get_serializer_context()
        report_id = self.kwargs.get('report_id')
        
        try:
            report = Report.objects.get(id=report_id)
            context['report'] = report
        except Report.DoesNotExist:
            pass
        
        return context
    
    def perform_create(self, serializer):
        """Create moderation action and update report status if needed."""
        user = self.request.user
        
        # Only allow staff/moderators to create actions
        if not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report_id = self.kwargs.get('report_id')
        
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response(
                {'error': 'Report not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the moderation action
        action = serializer.save(moderator=user, report=report)
        
        # Auto-assign moderator if not already assigned
        if not report.assigned_moderator:
            report.assign_moderator(user)
        
        # Update report status based on action type
        action_type = action.action_type
        if action_type in ['content_removed', 'account_suspended', 'account_banned']:
            if report.status != 'resolved':
                report.resolve(user, f"Action taken: {action.get_action_type_display()}")
        elif action_type == 'no_action':
            if report.status != 'dismissed':
                report.dismiss(user, "No action required")


class ModerationActionListView(generics.ListAPIView):
    """
    List moderation actions for a specific report.
    Available to moderators and staff only.
    """
    serializer_class = ModerationActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get moderation actions for the specified report."""
        user = self.request.user
        
        # Only allow staff/moderators to view actions
        if not (user.is_staff or user.is_superuser):
            return ModerationAction.objects.none()
        
        report_id = self.kwargs.get('report_id')
        return ModerationAction.objects.filter(
            report_id=report_id
        ).select_related('moderator')


class ModeratorDashboardView(generics.GenericAPIView):
    """
    Dashboard view for moderators showing their assigned reports and recent actions.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get moderator dashboard data."""
        user = request.user
        
        # Only allow staff/moderators to access dashboard
        if not (user.is_staff or user.is_superuser):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get assigned reports
        assigned_reports = Report.objects.filter(
            assigned_moderator=user,
            status__in=['under_review', 'escalated']
        ).select_related('reporter', 'content_type')[:10]
        
        # Get recent actions by this moderator
        recent_actions = ModerationAction.objects.filter(
            moderator=user
        ).select_related('report')[:10]
        
        # Get pending reports (unassigned)
        pending_reports = Report.objects.filter(
            status='pending'
        ).select_related('reporter', 'content_type')[:10]
        
        # Serialize data
        assigned_reports_data = ReportListSerializer(assigned_reports, many=True).data
        recent_actions_data = ModerationActionSerializer(recent_actions, many=True).data
        pending_reports_data = ReportListSerializer(pending_reports, many=True).data
        
        dashboard_data = {
            'assigned_reports': assigned_reports_data,
            'recent_actions': recent_actions_data,
            'pending_reports': pending_reports_data,
            'summary': {
                'assigned_count': Report.objects.filter(assigned_moderator=user, status__in=['under_review', 'escalated']).count(),
                'resolved_today': Report.objects.filter(resolved_by=user, resolved_at__date=timezone.now().date()).count(),
                'actions_today': ModerationAction.objects.filter(moderator=user, created_at__date=timezone.now().date()).count(),
            }
        }
        
        return Response(dashboard_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_assign_reports(request):
    """
    Bulk assign reports to moderators.
    """
    user = request.user
    
    # Only allow staff/moderators to bulk assign
    if not (user.is_staff or user.is_superuser):
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    report_ids = request.data.get('report_ids', [])
    moderator_id = request.data.get('moderator_id')
    
    if not report_ids:
        return Response(
            {'error': 'No report IDs provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get moderator (default to current user if not specified)
    if moderator_id:
        try:
            moderator = User.objects.get(id=moderator_id, is_staff=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid moderator ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        moderator = user
    
    # Update reports
    updated_count = 0
    for report_id in report_ids:
        try:
            report = Report.objects.get(id=report_id, status='pending')
            report.assign_moderator(moderator)
            updated_count += 1
        except Report.DoesNotExist:
            continue
    
    return Response({
        'message': f'{updated_count} reports assigned to {moderator.username}',
        'updated_count': updated_count
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_resolve_reports(request):
    """
    Bulk resolve reports with the same action.
    """
    user = request.user
    
    # Only allow staff/moderators to bulk resolve
    if not (user.is_staff or user.is_superuser):
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    report_ids = request.data.get('report_ids', [])
    action_type = request.data.get('action_type', 'no_action')
    resolution_notes = request.data.get('resolution_notes', '')
    
    if not report_ids:
        return Response(
            {'error': 'No report IDs provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    updated_count = 0
    for report_id in report_ids:
        try:
            report = Report.objects.get(
                id=report_id,
                status__in=['pending', 'under_review', 'escalated']
            )
            
            # Create moderation action
            ModerationAction.log_action(
                report=report,
                moderator=user,
                action_type=action_type,
                description=resolution_notes or f"Bulk action: {action_type}"
            )
            
            # Resolve report
            if action_type == 'no_action':
                report.dismiss(user, resolution_notes)
            else:
                report.resolve(user, resolution_notes)
            
            updated_count += 1
        except Report.DoesNotExist:
            continue
    
    return Response({
        'message': f'{updated_count} reports resolved',
        'updated_count': updated_count
    })
