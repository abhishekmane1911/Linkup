"""
Management command to check data integrity.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.common.integrity import run_integrity_check, fix_count_inconsistencies


class Command(BaseCommand):
    help = 'Check data integrity and consistency across the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix count inconsistencies',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f'Starting data integrity check at {timezone.now()}')
        )
        
        # Run integrity check
        results = run_integrity_check()
        
        # Display results
        if results['total_errors'] == 0 and results['total_warnings'] == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ No integrity issues found!')
            )
        else:
            if results['total_errors'] > 0:
                self.stdout.write(
                    self.style.ERROR(f'Found {results["total_errors"]} errors:')
                )
                for error in results['errors']:
                    self.stdout.write(self.style.ERROR(f'  - {error}'))
            
            if results['total_warnings'] > 0:
                self.stdout.write(
                    self.style.WARNING(f'Found {results["total_warnings"]} warnings:')
                )
                for warning in results['warnings']:
                    self.stdout.write(self.style.WARNING(f'  - {warning}'))
        
        # Fix inconsistencies if requested
        if options['fix']:
            self.stdout.write('\nAttempting to fix count inconsistencies...')
            fixed_count = fix_count_inconsistencies()
            self.stdout.write(
                self.style.SUCCESS(f'Fixed {fixed_count} inconsistencies')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Data integrity check completed at {timezone.now()}')
        )