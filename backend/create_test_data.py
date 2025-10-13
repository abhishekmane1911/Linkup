#!/usr/bin/env python
"""
Script to create test data for the Linkup application.
Run this with: python manage.py shell < create_test_data.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkup_backend.settings.development')
django.setup()

from apps.authentication.models import User
from apps.tweets.models import Tweet
from django.utils import timezone
from datetime import timedelta

def create_test_data():
    print("Creating test data...")
    
    # Get or create the existing user
    try:
        user = User.objects.get(email='raj1@gmail.com')
        print(f"Found existing user: {user.username}")
    except User.DoesNotExist:
        print("User raj1@gmail.com not found. Please create it first.")
        return
    
    # Create some test tweets
    tweets_data = [
        {
            'content': 'Just finished setting up the Django backend! 🚀 Ready to build some amazing features.',
            'created_at': timezone.now() - timedelta(hours=2)
        },
        {
            'content': 'Working on the frontend integration with React and TypeScript. The developer experience is amazing! 💻',
            'created_at': timezone.now() - timedelta(hours=4)
        },
        {
            'content': 'Learning about JWT authentication and how to secure API endpoints. Security first! 🔐',
            'created_at': timezone.now() - timedelta(hours=6)
        },
        {
            'content': 'Building a Twitter-like social media platform from scratch. Excited to see it come together! #WebDev #Django #React',
            'created_at': timezone.now() - timedelta(days=1)
        },
        {
            'content': 'Just implemented real-time features with WebSockets. The future is now! ⚡',
            'created_at': timezone.now() - timedelta(days=2)
        }
    ]
    
    created_tweets = []
    for tweet_data in tweets_data:
        tweet, created = Tweet.objects.get_or_create(
            author=user,
            content=tweet_data['content'],
            defaults={'created_at': tweet_data['created_at']}
        )
        if created:
            created_tweets.append(tweet)
            print(f"Created tweet: {tweet.content[:50]}...")
        else:
            print(f"Tweet already exists: {tweet.content[:50]}...")
    
    print(f"\nTest data creation complete!")
    print(f"Created {len(created_tweets)} new tweets")
    print(f"Total tweets for {user.username}: {Tweet.objects.filter(author=user).count()}")

if __name__ == '__main__':
    create_test_data()