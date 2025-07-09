from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.businesses.utils import update_all_business_metrics


class Command(BaseCommand):
    help = 'Update profile completeness and health status for all businesses'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of businesses to process in each batch'
        )
    
    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(f'Starting business metrics update at {start_time}')
        )
        
        try:
            updated_count = update_all_business_metrics()
            
            end_time = timezone.now()
            duration = end_time - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} businesses in {duration.total_seconds():.2f} seconds'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating business metrics: {str(e)}')
            )