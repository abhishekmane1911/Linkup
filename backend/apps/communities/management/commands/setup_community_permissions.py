from django.core.management.base import BaseCommand
from apps.communities.models import Permission, Role


class Command(BaseCommand):
    help = 'Set up default community permissions and roles'

    def handle(self, *args, **options):
        self.stdout.write('Setting up community permissions and roles...')
        
        # Create default permissions
        permissions_data = [
            {
                'name': 'Manage Community',
                'codename': 'manage_community',
                'description': 'Can edit community settings, description, and rules'
            },
            {
                'name': 'Manage Members',
                'codename': 'manage_members',
                'description': 'Can add, remove, and change member roles'
            },
            {
                'name': 'Manage Roles',
                'codename': 'manage_roles',
                'description': 'Can create and assign custom roles'
            },
            {
                'name': 'Moderate Content',
                'codename': 'moderate_content',
                'description': 'Can moderate posts and comments in the community'
            },
            {
                'name': 'Post Content',
                'codename': 'post_content',
                'description': 'Can create posts in the community'
            },
            {
                'name': 'Delete Posts',
                'codename': 'delete_posts',
                'description': 'Can delete posts and comments'
            },
            {
                'name': 'Ban Members',
                'codename': 'ban_members',
                'description': 'Can ban members from the community'
            },
            {
                'name': 'View Reports',
                'codename': 'view_reports',
                'description': 'Can view moderation reports'
            },
        ]
        
        created_permissions = []
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults={
                    'name': perm_data['name'],
                    'description': perm_data['description']
                }
            )
            if created:
                created_permissions.append(permission)
                self.stdout.write(f'Created permission: {permission.name}')
        
        # Create default roles
        roles_data = [
            {
                'name': 'Community Owner',
                'codename': 'community_owner',
                'description': 'Full control over the community',
                'permissions': [
                    'manage_community', 'manage_members', 'manage_roles',
                    'moderate_content', 'post_content', 'delete_posts',
                    'ban_members', 'view_reports'
                ],
                'is_default': True
            },
            {
                'name': 'Community Admin',
                'codename': 'community_admin',
                'description': 'Administrative privileges in the community',
                'permissions': [
                    'manage_members', 'manage_roles', 'moderate_content',
                    'post_content', 'delete_posts', 'ban_members', 'view_reports'
                ],
                'is_default': True
            },
            {
                'name': 'Community Moderator',
                'codename': 'community_moderator',
                'description': 'Content moderation privileges',
                'permissions': [
                    'moderate_content', 'post_content', 'delete_posts', 'view_reports'
                ],
                'is_default': True
            },
            {
                'name': 'Community Member',
                'codename': 'community_member',
                'description': 'Basic member privileges',
                'permissions': ['post_content'],
                'is_default': True
            },
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                codename=role_data['codename'],
                defaults={
                    'name': role_data['name'],
                    'description': role_data['description'],
                    'is_default': role_data['is_default']
                }
            )
            
            if created:
                self.stdout.write(f'Created role: {role.name}')
                
                # Assign permissions to role
                for perm_codename in role_data['permissions']:
                    try:
                        permission = Permission.objects.get(codename=perm_codename)
                        role.permissions.add(permission)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'Permission {perm_codename} not found')
                        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up community permissions and roles')
        )