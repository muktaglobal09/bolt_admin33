from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.crm.models import Lead


class Command(BaseCommand):
    help = 'Update lead scores for all leads'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of leads to process in each batch'
        )
        parser.add_argument(
            '--business-id',
            type=int,
            help='Update leads for specific business only'
        )
    
    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(f'Starting lead score update at {start_time}')
        )
        
        try:
            leads = Lead.objects.all()
            
            if options['business_id']:
                leads = leads.filter(business_id=options['business_id'])
            
            updated_count = 0
            batch_size = options['batch_size']
            
            for i in range(0, leads.count(), batch_size):
                batch = leads[i:i + batch_size]
                
                for lead in batch:
                    old_score = lead.lead_score
                    lead.calculate_lead_score()
                    
                    if lead.lead_score != old_score:
                        lead.save()
                        updated_count += 1
                        
                        self.stdout.write(
                            f'Updated lead {lead.id}: {old_score} -> {lead.lead_score}'
                        )
                
                self.stdout.write(f'Processed batch {i//batch_size + 1}')
            
            end_time = timezone.now()
            duration = end_time - start_time
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} leads in {duration.total_seconds():.2f} seconds'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating lead scores: {str(e)}')
            )