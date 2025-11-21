
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/tweets/", include("apps.tweets.urls")),
    path("api/v1/interactions/", include("apps.interactions.urls")),
    path("api/v1/messaging/", include("apps.messaging.urls")),
    path("api/v1/communities/", include("apps.communities.urls")),
    path("api/v1/moderation/", include("apps.moderation.urls")),
    path("api/v1/lists/", include("apps.lists.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
