from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import date, timedelta

from apps.businesses.models import Business, BusinessAnalytics
from apps.crm.models import Lead, CRMContact, CRMDeal
from apps.users.models import User
from apps.reviews.models import Review
from apps.payments.models import Payment, Subscription


class SearchhAdminSite(AdminSite):
    site_header = "Searchh Business Directory"
    site_title = "Searchh Admin"
    index_title = "Dashboard"
    
    # Override to ensure clean navigation
    def each_context(self, request):
        context = super().each_context(request)
        context.update({
            'site_header': self.site_header,
            'site_title': self.site_title,
            'index_title': self.index_title,
            'has_permission': request.user.is_active and request.user.is_staff,
        })
        return context
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """Custom dashboard view with comprehensive stats."""
        context = self.get_dashboard_context()
        return TemplateResponse(request, 'admin/dashboard.html', context)
    
    def get_dashboard_context(self):
        """Get comprehensive dashboard statistics."""
        # Business statistics
        total_businesses = Business.objects.count()
        verified_businesses = Business.objects.filter(verification_status='verified').count()
        featured_businesses = Business.objects.filter(is_featured=True).count()
        
        # CRM statistics
        total_leads = Lead.objects.count()
        qualified_leads = Lead.objects.filter(status='qualified').count()
        total_contacts = CRMContact.objects.count()
        total_deals = CRMDeal.objects.count()
        
        # User statistics
        total_users = User.objects.count()
        business_owners = User.objects.filter(user_type='business_owner').count()
        customers = User.objects.filter(user_type='customer').count()
        
        # Review statistics
        total_reviews = Review.objects.count()
        approved_reviews = Review.objects.filter(is_approved=True).count()
        
        # Payment statistics
        total_payments = Payment.objects.filter(status='completed').count()
        total_revenue = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Today's activity
        today = date.today()
        today_businesses = Business.objects.filter(created_at__date=today).count()
        today_leads = Lead.objects.filter(created_at__date=today).count()
        today_reviews = Review.objects.filter(created_at__date=today).count()
        
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
        
        # Recent activities
        recent_businesses = Business.objects.select_related('category', 'owner').order_by('-created_at')[:5]
        recent_leads = Lead.objects.select_related('business').order_by('-created_at')[:5]
        recent_reviews = Review.objects.select_related('business', 'user').order_by('-created_at')[:5]
        
        return {
            'title': 'Dashboard',
            'stats': {
                'total_businesses': total_businesses,
                'verified_businesses': verified_businesses,
                'featured_businesses': featured_businesses,
                'total_leads': total_leads,
                'qualified_leads': qualified_leads,
                'total_contacts': total_contacts,
                'total_deals': total_deals,
                'total_users': total_users,
                'business_owners': business_owners,
                'customers': customers,
                'total_reviews': total_reviews,
                'approved_reviews': approved_reviews,
                'total_payments': total_payments,
                'total_revenue': total_revenue,
                'today_businesses': today_businesses,
                'today_leads': today_leads,
                'today_reviews': today_reviews,
                'verification_rate': round((verified_businesses / total_businesses) * 100, 2) if total_businesses > 0 else 0,
                'lead_conversion_rate': round((qualified_leads / total_leads) * 100, 2) if total_leads > 0 else 0,
                'review_approval_rate': round((approved_reviews / total_reviews) * 100, 2) if total_reviews > 0 else 0,
            },
            'recent_businesses': recent_businesses,
            'recent_leads': recent_leads,
            'recent_reviews': recent_reviews,
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
    
    def index(self, request, extra_context=None):
        """Custom admin index with dashboard stats."""
        extra_context = extra_context or {}
        
        # Add basic stats to the main index
        dashboard_context = self.get_dashboard_context()
        extra_context.update({
            'stats': dashboard_context['stats'],
            'recent_businesses': dashboard_context['recent_businesses'][:3],
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance and replace default
admin_site = SearchhAdminSite(name='admin')

# Auto-register all models from our apps
from django.apps import apps
from django.contrib.admin.sites import site

for app_config in apps.get_app_configs():
    if app_config.name.startswith('apps.'):
        for model in app_config.get_models():
            if site.is_registered(model):
                admin_class = site._registry[model].__class__
                try:
                    admin_site.register(model, admin_class)
                except admin.sites.AlreadyRegistered:
                    pass

# Replace default admin site
admin.site = admin_site