from django.contrib import admin
from django.utils.html import format_html
from .models import Report, ModerationAction


class ModerationActionInline(admin.TabularInline):
    """
    Inline admin for moderation actions within report admin.
    """
    model = ModerationAction
    extra = 0
    readonly_fields = ['moderator', 'created_at']
    fields = ['action_type', 'description', 'severity_level', 'moderator', 'created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Admin interface for Report model.
    """
    inlines = [ModerationActionInline]
    list_display = [
        'id', 'reporter', 'report_type', 'content_type', 'object_id',
        'status', 'assigned_moderator', 'created_at'
    ]
    list_filter = [
        'status', 'report_type', 'content_type', 'created_at'
    ]
    search_fields = [
        'reporter__username', 'reporter__email',
        'description', 'resolution_notes'
    ]
    readonly_fields = [
        'reporter', 'content_type', 'object_id', 'created_at',
        'updated_at', 'resolved_at', 'reported_content_preview'
    ]
    fieldsets = (
        ('Report Information', {
            'fields': (
                'reporter', 'content_type', 'object_id',
                'report_type', 'description', 'reported_content_preview'
            )
        }),
        ('Status & Assignment', {
            'fields': (
                'status', 'assigned_moderator'
            )
        }),
        ('Resolution', {
            'fields': (
                'resolution_notes', 'resolved_by', 'resolved_at'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            )
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'reporter', 'assigned_moderator', 'resolved_by', 'content_type'
        )
    
    def save_model(self, request, obj, form, change):
        """Handle status changes when saving from admin."""
        if change:
            # If status is being changed to resolved/dismissed, set resolved_by
            if obj.status in ['resolved', 'dismissed'] and not obj.resolved_by:
                obj.resolved_by = request.user
        
        super().save_model(request, obj, form, change)
    
    actions = ['assign_to_me', 'mark_resolved', 'mark_dismissed']
    
    def assign_to_me(self, request, queryset):
        """Assign selected reports to the current user."""
        updated = queryset.filter(
            status__in=['pending', 'under_review']
        ).update(
            assigned_moderator=request.user,
            status='under_review'
        )
        self.message_user(
            request,
            f'{updated} reports assigned to you.'
        )
    assign_to_me.short_description = "Assign selected reports to me"
    
    def mark_resolved(self, request, queryset):
        """Mark selected reports as resolved."""
        updated = 0
        for report in queryset.filter(status__in=['pending', 'under_review', 'escalated']):
            report.resolve(request.user, "Resolved via admin action")
            updated += 1
        
        self.message_user(
            request,
            f'{updated} reports marked as resolved.'
        )
    mark_resolved.short_description = "Mark selected reports as resolved"
    
    def mark_dismissed(self, request, queryset):
        """Mark selected reports as dismissed."""
        updated = 0
        for report in queryset.filter(status__in=['pending', 'under_review', 'escalated']):
            report.dismiss(request.user, "Dismissed via admin action")
            updated += 1
        
        self.message_user(
            request,
            f'{updated} reports marked as dismissed.'
        )
    mark_dismissed.short_description = "Mark selected reports as dismissed"


@admin.register(ModerationAction)
class ModerationActionAdmin(admin.ModelAdmin):
    """
    Admin interface for ModerationAction model.
    """
    list_display = [
        'id', 'report', 'action_type', 'moderator',
        'severity_level', 'is_automated', 'created_at'
    ]
    list_filter = [
        'action_type', 'severity_level', 'is_automated', 'created_at'
    ]
    search_fields = [
        'report__id', 'moderator__username',
        'description'
    ]
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'report', 'moderator'
        )
