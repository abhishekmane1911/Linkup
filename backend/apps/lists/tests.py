from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import List, ListMember

User = get_user_model()


class ListModelTest(TestCase):
    """
    Test cases for List model.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
    
    def test_create_list(self):
        """Test creating a new list."""
        list_obj = List.objects.create(
            owner=self.user,
            name='Test List',
            description='A test list',
            privacy='public'
        )
        
        self.assertEqual(list_obj.name, 'Test List')
        self.assertEqual(list_obj.owner, self.user)
        self.assertEqual(list_obj.privacy, 'public')
        self.assertFalse(list_obj.is_deleted)
    
    def test_list_str_representation(self):
        """Test string representation of list."""
        list_obj = List.objects.create(
            owner=self.user,
            name='Test List'
        )
        
        expected_str = f"Test List by @{self.user.username}"
        self.assertEqual(str(list_obj), expected_str)
    
    def test_add_member_to_list(self):
        """Test adding a member to a list."""
        list_obj = List.objects.create(
            owner=self.user,
            name='Test List'
        )
        
        member, created = list_obj.add_member(self.other_user)
        
        self.assertTrue(created)
        self.assertTrue(list_obj.is_member(self.other_user))
        self.assertEqual(list_obj.members_count, 1)
    
    def test_remove_member_from_list(self):
        """Test removing a member from a list."""
        list_obj = List.objects.create(
            owner=self.user,
            name='Test List'
        )
        
        # Add member first
        list_obj.add_member(self.other_user)
        self.assertTrue(list_obj.is_member(self.other_user))
        
        # Remove member
        removed = list_obj.remove_member(self.other_user)
        
        self.assertTrue(removed)
        self.assertFalse(list_obj.is_member(self.other_user))
        self.assertEqual(list_obj.members_count, 0)
    
    def test_list_permissions(self):
        """Test list permission methods."""
        public_list = List.objects.create(
            owner=self.user,
            name='Public List',
            privacy='public'
        )
        
        private_list = List.objects.create(
            owner=self.user,
            name='Private List',
            privacy='private'
        )
        
        # Owner can view and edit both lists
        self.assertTrue(public_list.can_view(self.user))
        self.assertTrue(public_list.can_edit(self.user))
        self.assertTrue(private_list.can_view(self.user))
        self.assertTrue(private_list.can_edit(self.user))
        
        # Other user can view public but not private
        self.assertTrue(public_list.can_view(self.other_user))
        self.assertFalse(public_list.can_edit(self.other_user))
        self.assertFalse(private_list.can_view(self.other_user))
        self.assertFalse(private_list.can_edit(self.other_user))


class ListAPITest(APITestCase):
    """
    Test cases for List API endpoints.
    """
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
    
    def test_create_list(self):
        """Test creating a list via API."""
        url = reverse('lists:list-list-create')
        data = {
            'name': 'Test List',
            'description': 'A test list',
            'privacy': 'public'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(List.objects.count(), 1)
        
        list_obj = List.objects.first()
        self.assertEqual(list_obj.name, 'Test List')
        self.assertEqual(list_obj.owner, self.user)
    
    def test_list_user_lists(self):
        """Test listing user's lists."""
        # Create some lists
        List.objects.create(owner=self.user, name='List 1')
        List.objects.create(owner=self.user, name='List 2')
        List.objects.create(owner=self.other_user, name='Other List')
        
        url = reverse('lists:list-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only user's lists
    
    def test_add_member_to_list(self):
        """Test adding a member to a list."""
        list_obj = List.objects.create(owner=self.user, name='Test List')
        
        url = reverse('lists:add-member', kwargs={'list_id': list_obj.id})
        data = {'user_id': self.other_user.id}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(list_obj.is_member(self.other_user))
    
    def test_unauthorized_list_access(self):
        """Test that unauthorized users cannot access private lists."""
        private_list = List.objects.create(
            owner=self.other_user,
            name='Private List',
            privacy='private'
        )
        
        url = reverse('lists:list-detail', kwargs={'id': private_list.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_timeline(self):
        """Test list timeline functionality."""
        # Create a list and add a member
        list_obj = List.objects.create(owner=self.user, name='Test List')
        list_obj.add_member(self.other_user)
        
        # Create a tweet by the list member
        from apps.tweets.models import Tweet
        tweet = Tweet.objects.create(
            author=self.other_user,
            content='Test tweet from list member'
        )
        
        url = reverse('lists:list-timeline', kwargs={'list_id': list_obj.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['content'], 'Test tweet from list member')
    
    def test_list_discovery(self):
        """Test list discovery functionality."""
        # Create some public lists
        List.objects.create(owner=self.user, name='Public List 1', privacy='public')
        List.objects.create(owner=self.other_user, name='Public List 2', privacy='public')
        
        url = reverse('lists:list-discovery')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('discovery', response.data)
        self.assertIn('popular', response.data['discovery'])
        self.assertIn('recent', response.data['discovery'])
        self.assertIn('active', response.data['discovery'])