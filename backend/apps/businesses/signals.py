from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    Business, BusinessImage, BusinessService, BusinessProduct, 
    BusinessDocument, BusinessAnalytics
)
from .utils import BusinessMetricsCalculator


@receiver(post_save, sender=Business)
def update_business_metrics(sender, instance, created, **kwargs):
    """Update business metrics when business is saved."""
    if not created:  # Only for updates, not creation
        # Update profile completeness
        instance.profile_completeness = BusinessMetricsCalculator.calculate_profile_completeness(instance)
        
        # Update health status
        health_score = BusinessMetricsCalculator.calculate_health_score(instance)
        instance.health_status = BusinessMetricsCalculator.determine_health_status(health_score)
        
        # Update last activity
        instance.last_activity_at = timezone.now()
        
        # Save without triggering signals again
        Business.objects.filter(pk=instance.pk).update(
            profile_completeness=instance.profile_completeness,
            health_status=instance.health_status,
            last_activity_at=instance.last_activity_at
        )


@receiver(post_save, sender=BusinessImage)
def update_business_on_image_change(sender, instance, created, **kwargs):
    """Update business metrics when images are added/updated."""
    business = instance.business
    business.last_activity_at = timezone.now()
    business.save()
    
    # Update subscription usage if image was added
    if created:
        try:
            subscription = business.subscription
            subscription.used_images += 1
            subscription.save()
        except:
            pass


@receiver(post_delete, sender=BusinessImage)
def update_business_on_image_delete(sender, instance, **kwargs):
    """Update business metrics when images are deleted."""
    business = instance.business
    business.last_activity_at = timezone.now()
    business.save()
    
    # Update subscription usage
    try:
        subscription = business.subscription
        subscription.used_images = max(0, subscription.used_images - 1)
        subscription.save()
    except:
        pass


@receiver(post_save, sender=BusinessService)
def update_business_on_service_change(sender, instance, created, **kwargs):
    """Update business metrics when services are added/updated."""
    business = instance.business
    business.last_activity_at = timezone.now()
    business.save()
    
    # Update subscription usage if service was added
    if created:
        try:
            subscription = business.subscription
            subscription.used_services += 1
            subscription.save()
        except:
            pass


@receiver(post_delete, sender=BusinessService)
def update_business_on_service_delete(sender, instance, **kwargs):
    """Update business metrics when services are deleted."""
    business = instance.business
    business.last_activity_at = timezone.now()
    business.save()
    
    # Update subscription usage
    try:
        subscription = business.subscription
        subscription.used_services = max(0, subscription.used_services - 1)
        subscription.save()
    except:
        pass


@receiver(post_save, sender=BusinessProduct)
def update_business_on_product_change(sender, instance, created, **kwargs):
    """Update business metrics when products are added/updated."""
    business = instance.business
    business.last_activity_at = timezone.now()
    business.save()
    
    # Update subscription usage if product was added
    if created:
        try:
            subscription = business.subscription
            subscription.used_products += 1
            subscription.save()
        except:
            pass


@receiver(post_delete, sender=BusinessProduct)
def update_business_on_product_delete(sender, instance, **kwargs):
    """Update business metrics when products are deleted."""
    business = instance.business
    business.last_activity_at = timezone.now()
    business.save()
    
    # Update subscription usage
    try:
        subscription = business.subscription
        subscription.used_products = max(0, subscription.used_products - 1)
        subscription.save()
    except:
        pass


@receiver(post_save, sender=BusinessDocument)
def update_business_on_document_change(sender, instance, created, **kwargs):
    """Update business metrics when documents are added/updated."""
    business = instance.business
    business.last_activity_at = timezone.now()
    business.save()