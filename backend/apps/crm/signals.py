from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Lead, CRMContact, CRMDeal, CRMActivity, CRMNote, CRMSettings


@receiver(post_save, sender=Lead)
def handle_lead_conversion(sender, instance, created, **kwargs):
    """Handle lead conversion to contact and deal."""
    if not created and instance.status == 'converted':
        try:
            settings = CRMSettings.objects.first()
            if settings and settings.auto_convert_leads:
                # Auto-convert qualified leads
                if instance.lead_score >= settings.lead_score_threshold and not instance.converted_to_contact:
                    # Create contact from lead
                    contact = CRMContact.objects.create(
                        account=instance.business,
                        first_name=instance.first_name,
                        last_name=instance.last_name,
                        email=instance.email,
                        phone_number=instance.phone_number,
                        company=instance.company,
                        designation=instance.designation,
                        contact_type='customer',
                        lead_source=instance.lead_source,
                        owner=instance.owner,
                        address_line_1=instance.address,
                        city=instance.city,
                        state=instance.state,
                        country=instance.country,
                        notes=instance.notes
                    )
                    
                    # Update lead with conversion info
                    instance.converted_to_contact = contact
                    instance.converted_at = timezone.now()
                    instance.save()
                    
                    # Optionally create a deal
                    if instance.lead_score >= 80:  # High-value leads get deals
                        deal = CRMDeal.objects.create(
                            account=instance.business,
                            contact=contact,
                            title=f"Opportunity - {contact.full_name}",
                            description=f"Auto-generated deal from lead conversion",
                            stage='prospecting',
                            priority='medium',
                            probability=settings.default_deal_probability,
                            owner=instance.owner,
                            assigned_to=instance.assigned_to,
                            lead_source=instance.lead_source
                        )
                        
                        instance.converted_to_deal = deal
                        instance.save()
        except Exception as e:
            # Log error but don't break the save
            print(f"Error in lead conversion: {e}")


@receiver(post_save, sender=CRMActivity)
def update_last_contacted_on_activity(sender, instance, created, **kwargs):
    """Update last_contacted field when activities are created or completed."""
    try:
        settings = CRMSettings.objects.first()
        if settings and settings.auto_update_last_contacted:
            now = timezone.now()
            
            # Update contact's last_contacted
            if instance.contact:
                instance.contact.last_contacted = now
                instance.contact.save()
            
            # Update deal's last_contacted
            if instance.deal:
                instance.deal.last_contacted = now
                instance.deal.save()
            
            # Update lead's last_contacted
            if instance.lead:
                instance.lead.last_contacted = now
                instance.lead.save()
    except Exception as e:
        print(f"Error updating last_contacted: {e}")


@receiver(post_save, sender=CRMNote)
def update_last_contacted_on_note(sender, instance, created, **kwargs):
    """Update last_contacted field when notes are created."""
    if created:
        try:
            settings = CRMSettings.objects.first()
            if settings and settings.auto_update_last_contacted:
                now = timezone.now()
                
                # Update contact's last_contacted
                if instance.contact:
                    instance.contact.last_contacted = now
                    instance.contact.save()
                
                # Update deal's last_contacted
                if instance.deal:
                    instance.deal.last_contacted = now
                    instance.deal.save()
                
                # Update lead's last_contacted
                if instance.lead:
                    instance.lead.last_contacted = now
                    instance.lead.save()
        except Exception as e:
            print(f"Error updating last_contacted from note: {e}")


@receiver(pre_save, sender=Lead)
def calculate_lead_score_on_save(sender, instance, **kwargs):
    """Calculate lead score before saving."""
    instance.calculate_lead_score()


@receiver(post_save, sender=CRMDeal)
def handle_deal_stage_change(sender, instance, created, **kwargs):
    """Handle deal stage changes and notifications."""
    if not created:
        try:
            settings = CRMSettings.objects.first()
            if settings and settings.notify_on_deal_stage_change:
                # Here you would implement notification logic
                # For now, we'll just update the probability based on stage
                stage_probabilities = {
                    'prospecting': 10,
                    'qualification': 25,
                    'needs_analysis': 40,
                    'proposal': 60,
                    'negotiation': 80,
                    'closed_won': 100,
                    'closed_lost': 0
                }
                
                if instance.stage in stage_probabilities:
                    instance.probability = stage_probabilities[instance.stage]
                    # Use update to avoid triggering signals again
                    CRMDeal.objects.filter(pk=instance.pk).update(probability=instance.probability)
        except Exception as e:
            print(f"Error handling deal stage change: {e}")


@receiver(post_save, sender=CRMContact)
def create_welcome_activity(sender, instance, created, **kwargs):
    """Create a welcome activity for new contacts."""
    if created:
        try:
            CRMActivity.objects.create(
                account=instance.account,
                contact=instance,
                activity_type='note',
                subject='New Contact Added',
                description=f'Contact {instance.full_name} was added to the CRM system.',
                status='completed',
                scheduled_at=timezone.now(),
                completed_at=timezone.now(),
                assigned_to=instance.owner
            )
        except Exception as e:
            print(f"Error creating welcome activity: {e}")


# Signal to ensure only one CRMSettings instance
@receiver(pre_save, sender=CRMSettings)
def ensure_single_crm_settings(sender, instance, **kwargs):
    """Ensure only one CRMSettings instance exists."""
    if not instance.pk and CRMSettings.objects.exists():
        raise ValueError("Only one CRM Settings instance is allowed")