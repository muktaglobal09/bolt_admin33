from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.crm.models import CRMActivity, CRMSettings


class Command(BaseCommand):
    help = 'Clean up old CRM activities based on settings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            help='Number of days to keep activities (overrides settings)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        try:
            settings = CRMSettings.objects.first()
            
            if options['days']:
                days_to_keep = options['days']
            elif settings:
                days_to_keep = settings.delete_old_activities_days
            else:
                days_to_keep = 730  # Default 2 years
            
            cutoff_date = timezone.now() - timedelta(days=days_to_keep)
            
            old_activities = CRMActivity.objects.filter(
                created_at__lt=cutoff_date,
                status='completed'
            )
            
            count = old_activities.count()
            
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(
                        f'DRY RUN: Would delete {count} activities older than {days_to_keep} days'
                    )
                )
                
                # Show sample of what would be deleted
                sample = old_activities[:10]
                for activity in sample:
                    self.stdout.write(f'  - {activity.subject} ({activity.created_at})')
                
                if count > 10:
                    self.stdout.write(f'  ... and {count - 10} more')
            else:
                deleted_count = old_activities.delete()[0]
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted {deleted_count} old activities'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error cleaning up activities: {str(e)}')
            )