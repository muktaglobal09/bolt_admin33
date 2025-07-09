from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta, date
from .models import Business, BusinessAnalytics


class BusinessMetricsCalculator:
    """Utility class for calculating business metrics and analytics."""
    
    @staticmethod
    def calculate_profile_completeness(business):
        """Calculate profile completeness percentage for a business."""
        total_weight = 100
        current_score = 0
        
        # Required fields (60% total weight)
        required_fields = {
            'name': 8,
            'description': 8,
            'phone_number': 8,
            'email': 8,
            'category': 6,
            'business_type': 6,
            'address_line_1': 4,
            'city': 4,
            'state': 4,
            'pincode': 4,
        }
        
        for field, weight in required_fields.items():
            if getattr(business, field):
                current_score += weight
        
        # Important optional fields (25% total weight)
        optional_fields = {
            'logo': 5,
            'cover_image': 4,
            'website': 3,
            'established_year': 3,
            'employee_count': 2,
            'gst_number': 3,
            'short_description': 3,
            'latitude': 1,
            'longitude': 1,
        }
        
        for field, weight in optional_fields.items():
            if getattr(business, field):
                current_score += weight
        
        # Additional content (15% total weight)
        # Services and products
        if business.services.filter(is_active=True).count() > 0:
            current_score += 5
        if business.products.filter(is_active=True).count() > 0:
            current_score += 5
        if business.images.count() > 0:
            current_score += 3
        if business.documents.filter(is_verified=True).count() > 0:
            current_score += 2
        
        return min(100, current_score)
    
    @staticmethod
    def calculate_health_score(business):
        """Calculate business health score."""
        score = 0
        
        # Profile completeness (40% weight)
        completeness_score = (business.profile_completeness / 100) * 40
        score += completeness_score
        
        # Verification status (30% weight)
        verification_scores = {
            'verified': 30,
            'pending': 15,
            'rejected': 0,
            'suspended': 0
        }
        score += verification_scores.get(business.verification_status, 0)
        
        # Reviews and ratings (20% weight)
        review_count = business.review_count
        avg_rating = business.average_rating or 0
        
        if review_count >= 20:
            score += 10
        elif review_count >= 10:
            score += 7
        elif review_count >= 5:
            score += 5
        elif review_count > 0:
            score += 2
        
        if avg_rating >= 4.5:
            score += 10
        elif avg_rating >= 4.0:
            score += 7
        elif avg_rating >= 3.5:
            score += 5
        elif avg_rating >= 3.0:
            score += 2
        
        # Activity and engagement (10% weight)
        if business.last_activity_at:
            days_since_activity = (timezone.now() - business.last_activity_at).days
            if days_since_activity <= 7:
                score += 10
            elif days_since_activity <= 30:
                score += 7
            elif days_since_activity <= 90:
                score += 3
        
        return min(100, score)
    
    @staticmethod
    def determine_health_status(score):
        """Determine health status based on score."""
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'average'
        elif score >= 30:
            return 'poor'
        else:
            return 'critical'
    
    @staticmethod
    def update_business_analytics(business, analytics_data):
        """Update or create daily analytics for a business."""
        today = date.today()
        analytics, created = BusinessAnalytics.objects.get_or_create(
            business=business,
            date=today,
            defaults=analytics_data
        )
        
        if not created:
            # Update existing analytics
            for key, value in analytics_data.items():
                if hasattr(analytics, key):
                    setattr(analytics, key, getattr(analytics, key) + value)
            analytics.save()
        
        return analytics
    
    @staticmethod
    def get_business_dashboard_data(business, days=30):
        """Get dashboard data for a business."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        analytics = BusinessAnalytics.objects.filter(
            business=business,
            date__range=[start_date, end_date]
        ).aggregate(
            total_views=Sum('page_views'),
            total_visitors=Sum('unique_visitors'),
            total_inquiries=Sum('inquiries'),
            total_leads=Sum('leads'),
            total_conversions=Sum('conversions'),
            avg_rating=Avg('average_rating')
        )
        
        # Calculate conversion rate
        conversion_rate = 0
        if analytics['total_leads'] and analytics['total_leads'] > 0:
            conversion_rate = (analytics['total_conversions'] / analytics['total_leads']) * 100
        
        return {
            'views': analytics['total_views'] or 0,
            'visitors': analytics['total_visitors'] or 0,
            'inquiries': analytics['total_inquiries'] or 0,
            'leads': analytics['total_leads'] or 0,
            'conversions': analytics['total_conversions'] or 0,
            'conversion_rate': round(conversion_rate, 2),
            'avg_rating': round(analytics['avg_rating'] or 0, 2),
            'review_count': business.review_count,
            'profile_completeness': business.profile_completeness,
            'health_status': business.health_status
        }
    
    @staticmethod
    def get_admin_dashboard_stats():
        """Get overall statistics for admin dashboard."""
        total_businesses = Business.objects.count()
        verified_businesses = Business.objects.filter(verification_status='verified').count()
        featured_businesses = Business.objects.filter(is_featured=True).count()
        
        # Health distribution
        health_distribution = Business.objects.values('health_status').annotate(
            count=Count('id')
        ).order_by('health_status')
        
        # Verification distribution
        verification_distribution = Business.objects.values('verification_status').annotate(
            count=Count('id')
        ).order_by('verification_status')
        
        # Recent activity
        today = date.today()
        recent_analytics = BusinessAnalytics.objects.filter(date=today).aggregate(
            total_views=Sum('page_views'),
            total_leads=Sum('leads'),
            total_conversions=Sum('conversions')
        )
        
        return {
            'total_businesses': total_businesses,
            'verified_businesses': verified_businesses,
            'featured_businesses': featured_businesses,
            'verification_rate': round((verified_businesses / total_businesses) * 100, 2) if total_businesses > 0 else 0,
            'health_distribution': list(health_distribution),
            'verification_distribution': list(verification_distribution),
            'today_views': recent_analytics['total_views'] or 0,
            'today_leads': recent_analytics['total_leads'] or 0,
            'today_conversions': recent_analytics['total_conversions'] or 0,
        }


class BusinessValidationService:
    """Service for validating business data and enforcing plan limits."""
    
    @staticmethod
    def validate_plan_limits(business, action_type, count=1):
        """Validate if business can perform action based on their plan limits."""
        try:
            subscription = business.subscription
            plan = subscription.plan
        except:
            # No subscription, use free plan limits
            return False, "No active subscription found"
        
        if not subscription.is_active or subscription.is_expired:
            return False, "Subscription is expired or inactive"
        
        # Check specific limits based on action type
        if action_type == 'add_image':
            if subscription.used_images + count > plan.max_images_per_business:
                return False, f"Image limit exceeded. Plan allows {plan.max_images_per_business} images."
        
        elif action_type == 'add_service':
            if subscription.used_services + count > plan.max_services_per_business:
                return False, f"Service limit exceeded. Plan allows {plan.max_services_per_business} services."
        
        elif action_type == 'add_product':
            if subscription.used_products + count > plan.max_products_per_business:
                return False, f"Product limit exceeded. Plan allows {plan.max_products_per_business} products."
        
        elif action_type == 'use_lead_credit':
            if subscription.used_lead_credits + count > plan.monthly_lead_credits:
                return False, f"Lead credit limit exceeded. Plan allows {plan.monthly_lead_credits} lead credits per month."
        
        return True, "Action allowed"
    
    @staticmethod
    def update_usage_count(business, action_type, count=1):
        """Update usage count for a business subscription."""
        try:
            subscription = business.subscription
            
            if action_type == 'add_image':
                subscription.used_images += count
            elif action_type == 'add_service':
                subscription.used_services += count
            elif action_type == 'add_product':
                subscription.used_products += count
            elif action_type == 'use_lead_credit':
                subscription.used_lead_credits += count
            
            subscription.save()
            return True
        except:
            return False


def update_all_business_metrics():
    """Management command function to update all business metrics."""
    businesses = Business.objects.all()
    updated_count = 0
    
    for business in businesses:
        # Update profile completeness
        business.profile_completeness = BusinessMetricsCalculator.calculate_profile_completeness(business)
        
        # Update health status
        health_score = BusinessMetricsCalculator.calculate_health_score(business)
        business.health_status = BusinessMetricsCalculator.determine_health_status(health_score)
        
        business.save()
        updated_count += 1
    
    return updated_count