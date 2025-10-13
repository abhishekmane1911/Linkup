"""
Custom validators for the Linkup backend.
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def validate_username(value):
    """
    Validate username format.
    Username must be 3-30 characters, alphanumeric and underscores only.
    """
    if len(value) < 3:
        raise ValidationError(_('Username must be at least 3 characters long.'))
    if len(value) > 30:
        raise ValidationError(_('Username must be no more than 30 characters long.'))
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError(_('Username can only contain letters, numbers, and underscores.'))


def validate_tweet_content(value):
    """
    Validate tweet content.
    Tweet must be 1-280 characters.
    """
    if not value or not value.strip():
        raise ValidationError(_('Tweet content cannot be empty.'))
    if len(value) > 280:
        raise ValidationError(_('Tweet content must be no more than 280 characters.'))


def validate_bio_length(value):
    """
    Validate user bio length.
    Bio must be no more than 160 characters.
    """
    if value and len(value) > 160:
        raise ValidationError(_('Bio must be no more than 160 characters.'))


def validate_community_name(value):
    """
    Validate community name format.
    Community name must be 3-50 characters.
    """
    if len(value) < 3:
        raise ValidationError(_('Community name must be at least 3 characters long.'))
    if len(value) > 50:
        raise ValidationError(_('Community name must be no more than 50 characters long.'))


def validate_hashtag(value):
    """
    Validate hashtag format.
    Hashtag must start with # and contain only alphanumeric characters and underscores.
    """
    if not value.startswith('#'):
        raise ValidationError(_('Hashtag must start with #.'))
    
    hashtag_content = value[1:]  # Remove the #
    if len(hashtag_content) < 1:
        raise ValidationError(_('Hashtag cannot be empty.'))
    if len(hashtag_content) > 100:
        raise ValidationError(_('Hashtag must be no more than 100 characters long.'))
    if not re.match(r'^[a-zA-Z0-9_]+$', hashtag_content):
        raise ValidationError(_('Hashtag can only contain letters, numbers, and underscores.'))


def validate_file_size(value):
    """
    Validate uploaded file size.
    Maximum file size is 10MB.
    """
    max_size = 10 * 1024 * 1024  # 10MB
    if value.size > max_size:
        raise ValidationError(_('File size must be no more than 10MB.'))


def validate_image_file(value):
    """
    Validate that uploaded file is an image.
    """
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if value.content_type not in allowed_types:
        raise ValidationError(_('File must be a valid image (JPEG, PNG, GIF, or WebP).'))
    
    # Also validate file size
    validate_file_size(value)


def validate_video_file(value):
    """
    Validate that uploaded file is a video.
    """
    allowed_types = ['video/mp4', 'video/webm', 'video/ogg']
    if value.content_type not in allowed_types:
        raise ValidationError(_('File must be a valid video (MP4, WebM, or OGG).'))
    
    # Video files can be larger, up to 50MB
    max_size = 50 * 1024 * 1024  # 50MB
    if value.size > max_size:
        raise ValidationError(_('Video file size must be no more than 50MB.'))


def validate_media_file(value):
    """
    Validate that uploaded file is either an image or video.
    """
    image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    video_types = ['video/mp4', 'video/webm', 'video/ogg']
    
    if value.content_type in image_types:
        validate_image_file(value)
    elif value.content_type in video_types:
        validate_video_file(value)
    else:
        raise ValidationError(_('File must be a valid image or video.'))


# Regex validators
username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]+$',
    message=_('Username can only contain letters, numbers, and underscores.'),
    code='invalid_username'
)

hashtag_validator = RegexValidator(
    regex=r'^#[a-zA-Z0-9_]+$',
    message=_('Hashtag must start with # and contain only letters, numbers, and underscores.'),
    code='invalid_hashtag'
)