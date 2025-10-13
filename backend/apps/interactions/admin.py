from django.contrib import admin
from .models import Like, Retweet, Bookmark, Follow


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'tweet', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'tweet__content']
    readonly_fields = ['created_at']


@admin.register(Retweet)
class RetweetAdmin(admin.ModelAdmin):
    list_display = ['user', 'tweet', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'tweet__content']
    readonly_fields = ['created_at']


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'tweet', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'tweet__content']
    readonly_fields = ['created_at']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['created_at']
