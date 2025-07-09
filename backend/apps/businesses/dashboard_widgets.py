from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import date, timedelta
from .models import Business, BusinessAnalytics
from .utils import BusinessMetricsCalculator


class BusinessDashboardMixin:
    """Mixin to add business dashboard functionality to admin."""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('business-dashboard/', self.business_dashboard_view, name='business_dashboard'),
        ]
        return custom_urls + urls
    
    def business_dashboard_view(self, request):
        """Custom dashboard view for business analytics."""
        context = self.get_dashboard_context()
        return TemplateResponse(request, 'admin/business_dashboard.html', context)
    
    def get_dashboard_context(self):
        """Get context data for business dashboard."""
        # Overall statistics
        stats = BusinessMetricsCalculator.get_admin_dashboard_stats()
        
        # Recent businesses
        recent_businesses = Business.objects.select_related('category', 'owner').order_by('-created_at')[:10]
        
        # Top performing businesses
        top_businesses = Business.objects.filter(
            verification_status='verified'
        ).order_by('-view_count', '-lead_count')[:10]
        
        # Businesses needing attention
        attention_businesses = Business.objects.filter(
            Q(health_status__in=['poor', 'critical']) |
            Q(verification_status='pending') |
            Q(profile_completeness__lt=50)
        ).order_by('health_status', 'profile_completeness')[:10]
        
        # Analytics for last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        daily_analytics = BusinessAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).values('date').annotate(
            total_views=Sum('page_views'),
            total_leads=Sum('leads'),
            total_conversions=Sum('conversions')
        ).order_by('date')
        
        return {
            'title': 'Business Dashboard',
            'stats': stats,
            'recent_businesses': recent_businesses,
            'top_businesses': top_businesses,
            'attention_businesses': attention_businesses,
            'daily_analytics': list(daily_analytics),
            'chart_data': self.prepare_chart_data(daily_analytics),
        }
    
    def prepare_chart_data(self, analytics_data):
        """Prepare data for dashboard charts."""
        dates = []
        views = []
        leads = []
        conversions = []
        
        for item in analytics_data:
            dates.append(item['date'].strftime('%Y-%m-%d'))
            views.append(item['total_views'] or 0)
            leads.append(item['total_leads'] or 0)
            conversions.append(item['total_conversions'] or 0)
        
        return {
            'dates': dates,
            'views': views,
            'leads': leads,
            'conversions': conversions,
        }


# Custom admin site with dashboard
class BusinessAdminSite(BusinessDashboardMixin, AdminSite):
    site_header = "Searchh Business Directory Admin"
    site_title = "Searchh Admin"
    index_title = "Business Directory Management"
    
    def index(self, request, extra_context=None):
        """Custom admin index with business dashboard."""
        extra_context = extra_context or {}
        
        # Add dashboard widgets to context
        dashboard_context = self.get_dashboard_context()
        extra_context.update(dashboard_context)
        
        return super().index(request, extra_context)


# Create custom admin site instance
business_admin_site = BusinessAdminSite(name='business_admin')