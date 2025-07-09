from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta, date
from .models import Lead, CRMContact, CRMDeal, CRMActivity, CRMTask


class CRMAnalytics:
    """Utility class for CRM analytics and reporting."""
    
    @staticmethod
    def get_lead_analytics(business, days=30):
        """Get lead analytics for a business."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        leads = Lead.objects.filter(business=business, created_at__range=[start_date, end_date])
        
        analytics = {
            'total_leads': leads.count(),
            'new_leads': leads.filter(status='new').count(),
            'qualified_leads': leads.filter(status='qualified').count(),
            'converted_leads': leads.filter(status='converted').count(),
            'lost_leads': leads.filter(status='lost').count(),
            'conversion_rate': 0,
            'avg_lead_score': leads.aggregate(avg_score=Avg('lead_score'))['avg_score'] or 0,
            'lead_sources': leads.values('lead_source').annotate(count=Count('id')).order_by('-count'),
            'daily_leads': []
        }
        
        if analytics['total_leads'] > 0:
            analytics['conversion_rate'] = (analytics['converted_leads'] / analytics['total_leads']) * 100
        
        # Daily breakdown
        for i in range(days):
            day = end_date - timedelta(days=i)
            day_leads = leads.filter(created_at__date=day.date()).count()
            analytics['daily_leads'].append({
                'date': day.date(),
                'count': day_leads
            })
        
        return analytics
    
    @staticmethod
    def get_deal_analytics(business, days=30):
        """Get deal analytics for a business."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        deals = CRMDeal.objects.filter(account=business, created_at__range=[start_date, end_date])
        
        analytics = {
            'total_deals': deals.count(),
            'total_value': deals.aggregate(total=Sum('value'))['total'] or 0,
            'avg_deal_value': deals.aggregate(avg=Avg('value'))['avg'] or 0,
            'won_deals': deals.filter(stage='closed_won').count(),
            'lost_deals': deals.filter(stage='closed_lost').count(),
            'active_deals': deals.exclude(stage__in=['closed_won', 'closed_lost']).count(),
            'win_rate': 0,
            'pipeline_value': deals.exclude(stage__in=['closed_won', 'closed_lost']).aggregate(total=Sum('value'))['total'] or 0,
            'stage_distribution': deals.values('stage').annotate(count=Count('id')).order_by('-count'),
            'monthly_forecast': 0
        }
        
        closed_deals = analytics['won_deals'] + analytics['lost_deals']
        if closed_deals > 0:
            analytics['win_rate'] = (analytics['won_deals'] / closed_deals) * 100
        
        # Calculate forecast based on probability
        forecast_deals = deals.exclude(stage__in=['closed_won', 'closed_lost'])
        for deal in forecast_deals:
            if deal.value and deal.probability:
                analytics['monthly_forecast'] += (deal.value * deal.probability / 100)
        
        return analytics
    
    @staticmethod
    def get_activity_analytics(business, days=30):
        """Get activity analytics for a business."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        activities = CRMActivity.objects.filter(account=business, created_at__range=[start_date, end_date])
        
        analytics = {
            'total_activities': activities.count(),
            'completed_activities': activities.filter(status='completed').count(),
            'pending_activities': activities.filter(status='planned').count(),
            'overdue_activities': activities.filter(status='overdue').count(),
            'completion_rate': 0,
            'activity_types': activities.values('activity_type').annotate(count=Count('id')).order_by('-count'),
            'daily_activities': []
        }
        
        if analytics['total_activities'] > 0:
            analytics['completion_rate'] = (analytics['completed_activities'] / analytics['total_activities']) * 100
        
        # Daily breakdown
        for i in range(days):
            day = end_date - timedelta(days=i)
            day_activities = activities.filter(created_at__date=day.date()).count()
            analytics['daily_activities'].append({
                'date': day.date(),
                'count': day_activities
            })
        
        return analytics
    
    @staticmethod
    def get_task_analytics(business, days=30):
        """Get task analytics for a business."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        tasks = CRMTask.objects.filter(account=business, created_at__range=[start_date, end_date])
        
        analytics = {
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='completed').count(),
            'pending_tasks': tasks.filter(status='pending').count(),
            'overdue_tasks': tasks.filter(due_date__lt=timezone.now(), status__in=['pending', 'in_progress']).count(),
            'completion_rate': 0,
            'avg_completion_time': 0,
            'task_priorities': tasks.values('priority').annotate(count=Count('id')).order_by('-count'),
            'task_types': tasks.values('task_type').annotate(count=Count('id')).order_by('-count')
        }
        
        if analytics['total_tasks'] > 0:
            analytics['completion_rate'] = (analytics['completed_tasks'] / analytics['total_tasks']) * 100
        
        # Calculate average completion time
        completed_tasks = tasks.filter(status='completed', completed_at__isnull=False)
        if completed_tasks.exists():
            total_time = 0
            count = 0
            for task in completed_tasks:
                if task.completed_at and task.created_at:
                    time_diff = task.completed_at - task.created_at
                    total_time += time_diff.total_seconds()
                    count += 1
            
            if count > 0:
                analytics['avg_completion_time'] = total_time / count / 3600  # Convert to hours
        
        return analytics
    
    @staticmethod
    def get_performance_analytics(business, user=None, days=30):
        """Get performance analytics for a business or specific user."""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base filters
        lead_filter = Q(business=business, created_at__range=[start_date, end_date])
        deal_filter = Q(account=business, created_at__range=[start_date, end_date])
        activity_filter = Q(account=business, created_at__range=[start_date, end_date])
        
        # Add user filter if specified
        if user:
            lead_filter &= Q(assigned_to=user)
            deal_filter &= Q(assigned_to=user)
            activity_filter &= Q(assigned_to=user)
        
        leads = Lead.objects.filter(lead_filter)
        deals = CRMDeal.objects.filter(deal_filter)
        activities = CRMActivity.objects.filter(activity_filter)
        
        analytics = {
            'leads_generated': leads.count(),
            'leads_converted': leads.filter(status='converted').count(),
            'deals_created': deals.count(),
            'deals_won': deals.filter(stage='closed_won').count(),
            'total_deal_value': deals.filter(stage='closed_won').aggregate(total=Sum('value'))['total'] or 0,
            'activities_completed': activities.filter(status='completed').count(),
            'calls_made': activities.filter(activity_type='call', status='completed').count(),
            'meetings_held': activities.filter(activity_type='meeting', status='completed').count(),
            'emails_sent': activities.filter(activity_type='email', status='completed').count(),
        }
        
        # Calculate conversion rates
        if analytics['leads_generated'] > 0:
            analytics['lead_conversion_rate'] = (analytics['leads_converted'] / analytics['leads_generated']) * 100
        else:
            analytics['lead_conversion_rate'] = 0
        
        if analytics['deals_created'] > 0:
            analytics['deal_win_rate'] = (analytics['deals_won'] / analytics['deals_created']) * 100
        else:
            analytics['deal_win_rate'] = 0
        
        return analytics
    
    @staticmethod
    def get_pipeline_analytics(business):
        """Get sales pipeline analytics."""
        deals = CRMDeal.objects.filter(account=business).exclude(stage__in=['closed_won', 'closed_lost'])
        
        pipeline_data = []
        stages = ['prospecting', 'qualification', 'needs_analysis', 'proposal', 'negotiation']
        
        for stage in stages:
            stage_deals = deals.filter(stage=stage)
            stage_value = stage_deals.aggregate(total=Sum('value'))['total'] or 0
            
            pipeline_data.append({
                'stage': stage,
                'stage_display': stage.replace('_', ' ').title(),
                'deal_count': stage_deals.count(),
                'total_value': stage_value,
                'avg_value': stage_deals.aggregate(avg=Avg('value'))['avg'] or 0,
                'deals': list(stage_deals.values('id', 'title', 'value', 'probability', 'expected_close_date'))
            })
        
        return {
            'pipeline_stages': pipeline_data,
            'total_pipeline_value': deals.aggregate(total=Sum('value'))['total'] or 0,
            'total_pipeline_deals': deals.count(),
            'weighted_pipeline_value': sum([
                (deal.value or 0) * (deal.probability or 0) / 100 
                for deal in deals if deal.value and deal.probability
            ])
        }
    
    @staticmethod
    def get_forecast_analytics(business, months=3):
        """Get sales forecast analytics."""
        from dateutil.relativedelta import relativedelta
        
        today = date.today()
        forecast_data = []
        
        for i in range(months):
            month_start = today + relativedelta(months=i)
            month_end = month_start + relativedelta(months=1) - timedelta(days=1)
            
            # Deals expected to close in this month
            month_deals = CRMDeal.objects.filter(
                account=business,
                expected_close_date__range=[month_start, month_end]
            ).exclude(stage__in=['closed_won', 'closed_lost'])
            
            # Calculate forecast based on probability
            forecast_value = 0
            best_case = 0
            worst_case = 0
            
            for deal in month_deals:
                if deal.value:
                    best_case += deal.value
                    if deal.probability:
                        forecast_value += (deal.value * deal.probability / 100)
                        if deal.probability >= 75:  # High probability deals
                            worst_case += deal.value
            
            forecast_data.append({
                'month': month_start.strftime('%B %Y'),
                'month_date': month_start,
                'deal_count': month_deals.count(),
                'forecast_value': forecast_value,
                'best_case': best_case,
                'worst_case': worst_case,
                'deals': list(month_deals.values('id', 'title', 'value', 'probability', 'stage'))
            })
        
        return {
            'forecast_months': forecast_data,
            'total_forecast': sum([month['forecast_value'] for month in forecast_data]),
            'total_best_case': sum([month['best_case'] for month in forecast_data]),
            'total_worst_case': sum([month['worst_case'] for month in forecast_data])
        }


class CRMReportGenerator:
    """Generate various CRM reports."""
    
    @staticmethod
    def generate_leads_report(business, filters=None):
        """Generate leads report."""
        leads = Lead.objects.filter(business=business)
        
        if filters:
            if filters.get('status'):
                leads = leads.filter(status=filters['status'])
            if filters.get('lead_source'):
                leads = leads.filter(lead_source=filters['lead_source'])
            if filters.get('date_from'):
                leads = leads.filter(created_at__gte=filters['date_from'])
            if filters.get('date_to'):
                leads = leads.filter(created_at__lte=filters['date_to'])
        
        return {
            'total_leads': leads.count(),
            'status_breakdown': leads.values('status').annotate(count=Count('id')),
            'source_breakdown': leads.values('lead_source').annotate(count=Count('id')),
            'avg_lead_score': leads.aggregate(avg=Avg('lead_score'))['avg'] or 0,
            'conversion_rate': (leads.filter(status='converted').count() / leads.count() * 100) if leads.count() > 0 else 0,
            'leads_data': list(leads.values(
                'id', 'first_name', 'last_name', 'email', 'company',
                'status', 'lead_source', 'lead_score', 'created_at'
            ))
        }
    
    @staticmethod
    def generate_deals_report(business, filters=None):
        """Generate deals report."""
        deals = CRMDeal.objects.filter(account=business)
        
        if filters:
            if filters.get('stage'):
                deals = deals.filter(stage=filters['stage'])
            if filters.get('date_from'):
                deals = deals.filter(created_at__gte=filters['date_from'])
            if filters.get('date_to'):
                deals = deals.filter(created_at__lte=filters['date_to'])
        
        return {
            'total_deals': deals.count(),
            'total_value': deals.aggregate(total=Sum('value'))['total'] or 0,
            'avg_deal_value': deals.aggregate(avg=Avg('value'))['avg'] or 0,
            'stage_breakdown': deals.values('stage').annotate(count=Count('id')),
            'won_deals': deals.filter(stage='closed_won').count(),
            'lost_deals': deals.filter(stage='closed_lost').count(),
            'win_rate': (deals.filter(stage='closed_won').count() / deals.count() * 100) if deals.count() > 0 else 0,
            'deals_data': list(deals.values(
                'id', 'title', 'contact__first_name', 'contact__last_name',
                'value', 'stage', 'probability', 'expected_close_date', 'created_at'
            ))
        }