from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

User = get_user_model()


class Report(models.Model):
    """
    Report model for content/user reports with generic foreign key support.
    """
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('violence', 'Violence'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('copyright', 'Copyright Violation'),
        ('fake_news', 'Fake News'),
        ('impersonation', 'Impersonation'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
        ('escalated', 'Escalated'),
    ]
    
    # Reporter information
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_made',
        help_text="User who submitted the report"
    )
    
    # Generic foreign key to support reporting different content types
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type of content being reported"
    )
    object_id = models.PositiveIntegerField(
        help_text="ID of the reported object"
    )
    reported_object = GenericForeignKey('content_type', 'object_id')
    
    # Report details
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPES,
        help_text="Type of violation being reported"
    )
    description = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Additional details about the report"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the report"
    )
    
    # Moderation information
    assigned_moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_reports',
        help_text="Moderator assigned to review this report"
    )
    
    # Resolution details
    resolution_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes from moderator about resolution"
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports',
        help_text="Moderator who resolved the report"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the report was resolved"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reporter']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['status']),
            models.Index(fields=['report_type']),
            models.Index(fields=['assigned_moderator']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['reporter', 'content_type', 'object_id']
    
    def __str__(self):
        return f"Report #{self.id} - {self.report_type} by @{self.reporter.username}"
    
    def save(self, *args, **kwargs):
        """Override save to handle status changes."""
        # Set resolved timestamp when status changes to resolved
        if self.status in ['resolved', 'dismissed'] and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def assign_moderator(self, moderator):
        """Assign a moderator to this report."""
        self.assigned_moderator = moderator
        self.status = 'under_review'
        self.save(update_fields=['assigned_moderator', 'status', 'updated_at'])
    
    def resolve(self, moderator, resolution_notes=None):
        """Mark report as resolved."""
        self.status = 'resolved'
        self.resolved_by = moderator
        self.resolved_at = timezone.now()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        self.save(update_fields=['status', 'resolved_by', 'resolved_at', 'resolution_notes', 'updated_at'])
    
    def dismiss(self, moderator, resolution_notes=None):
        """Mark report as dismissed."""
        self.status = 'dismissed'
        self.resolved_by = moderator
        self.resolved_at = timezone.now()
        if resolution_notes:
            self.resolution_notes = resolution_notes
        self.save(update_fields=['status', 'resolved_by', 'resolved_at', 'resolution_notes', 'updated_at'])
    
    def escalate(self):
        """Escalate report to higher level moderation."""
        self.status = 'escalated'
        self.save(update_fields=['status', 'updated_at'])
    
    @property
    def is_pending(self):
        """Check if report is pending review."""
        return self.status == 'pending'
    
    @property
    def is_resolved(self):
        """Check if report has been resolved."""
        return self.status in ['resolved', 'dismissed']
    
    @property
    def reported_content_preview(self):
        """Get a preview of the reported content."""
        if hasattr(self.reported_object, 'content'):
            content = self.reported_object.content
            return content[:100] + "..." if len(content) > 100 else content
        elif hasattr(self.reported_object, 'username'):
            return f"User: @{self.reported_object.username}"
        return "Content not available"


class ModerationAction(models.Model):
    """
    Model to track moderation actions taken on reports and content.
    """
    ACTION_TYPES = [
        ('no_action', 'No Action Required'),
        ('warning_issued', 'Warning Issued'),
        ('content_removed', 'Content Removed'),
        ('account_suspended', 'Account Suspended'),
        ('account_banned', 'Account Banned'),
        ('content_flagged', 'Content Flagged'),
        ('escalated', 'Escalated to Higher Authority'),
        ('other', 'Other Action'),
    ]
    
    # Related report
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='moderation_actions',
        help_text="Report this action is related to"
    )
    
    # Action details
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        help_text="Type of moderation action taken"
    )
    description = models.TextField(
        help_text="Detailed description of the action taken"
    )
    
    # Moderator information
    moderator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='moderation_actions',
        help_text="Moderator who took this action"
    )
    
    # Action metadata
    is_automated = models.BooleanField(
        default=False,
        help_text="Whether this action was taken automatically"
    )
    severity_level = models.IntegerField(
        choices=[
            (1, 'Low'),
            (2, 'Medium'),
            (3, 'High'),
            (4, 'Critical'),
        ],
        default=1,
        help_text="Severity level of the action"
    )
    
    # Additional data (JSON field for flexible storage)
    additional_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional data related to the action"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'moderation_actions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report']),
            models.Index(fields=['moderator']),
            models.Index(fields=['action_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['severity_level']),
        ]
    
    def __str__(self):
        return f"Action #{self.id} - {self.action_type} by @{self.moderator.username}"
    
    @classmethod
    def log_action(cls, report, moderator, action_type, description, severity_level=1, additional_data=None):
        """
        Class method to log a moderation action.
        """
        return cls.objects.create(
            report=report,
            moderator=moderator,
            action_type=action_type,
            description=description,
            severity_level=severity_level,
            additional_data=additional_data or {}
        )
    
    @property
    def severity_display(self):
        """Get human-readable severity level."""
        severity_map = {1: 'Low', 2: 'Medium', 3: 'High', 4: 'Critical'}
        return severity_map.get(self.severity_level, 'Unknown')
