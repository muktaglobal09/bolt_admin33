# Generated by Django 5.2.4 on 2025-07-06 19:08

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('businesses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CRMContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None)),
                ('company', models.CharField(blank=True, max_length=200)),
                ('designation', models.CharField(blank=True, max_length=100)),
                ('contact_type', models.CharField(choices=[('lead', 'Lead'), ('customer', 'Customer'), ('prospect', 'Prospect'), ('partner', 'Partner'), ('vendor', 'Vendor')], default='lead', max_length=20)),
                ('lead_source', models.CharField(blank=True, choices=[('website', 'Website'), ('referral', 'Referral'), ('social_media', 'Social Media'), ('advertisement', 'Advertisement'), ('cold_call', 'Cold Call'), ('email_campaign', 'Email Campaign'), ('trade_show', 'Trade Show'), ('other', 'Other')], max_length=20)),
                ('address_line_1', models.CharField(blank=True, max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('pincode', models.CharField(blank=True, max_length=10)),
                ('country', models.CharField(default='India', max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags', max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_contacts', to='businesses.business')),
            ],
            options={
                'verbose_name': 'CRM Contact',
                'verbose_name_plural': 'CRM Contacts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CRMDeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('currency', models.CharField(default='INR', max_length=3)),
                ('stage', models.CharField(choices=[('prospecting', 'Prospecting'), ('qualification', 'Qualification'), ('proposal', 'Proposal'), ('negotiation', 'Negotiation'), ('closed_won', 'Closed Won'), ('closed_lost', 'Closed Lost')], default='prospecting', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('probability', models.PositiveIntegerField(default=0, help_text='Probability of closing (0-100%)')),
                ('expected_close_date', models.DateField(blank=True, null=True)),
                ('actual_close_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_deals', to=settings.AUTH_USER_MODEL)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_deals', to='businesses.business')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='crm.crmcontact')),
            ],
            options={
                'verbose_name': 'CRM Deal',
                'verbose_name_plural': 'CRM Deals',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CRMActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('activity_type', models.CharField(choices=[('call', 'Phone Call'), ('email', 'Email'), ('meeting', 'Meeting'), ('task', 'Task'), ('note', 'Note'), ('sms', 'SMS'), ('other', 'Other')], max_length=20)),
                ('subject', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('overdue', 'Overdue')], default='planned', max_length=20)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('duration_minutes', models.PositiveIntegerField(blank=True, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_activities', to=settings.AUTH_USER_MODEL)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_activities', to='businesses.business')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='crm.crmcontact')),
                ('deal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='crm.crmdeal')),
            ],
            options={
                'verbose_name': 'CRM Activity',
                'verbose_name_plural': 'CRM Activities',
                'ordering': ['-scheduled_at', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CRMNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('content', models.TextField()),
                ('is_private', models.BooleanField(default=False)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_notes', to='businesses.business')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crm_notes', to='crm.crmcontact')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_notes', to=settings.AUTH_USER_MODEL)),
                ('deal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='crm_notes', to='crm.crmdeal')),
            ],
            options={
                'verbose_name': 'CRM Note',
                'verbose_name_plural': 'CRM Notes',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CRMTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('due_date', models.DateTimeField()),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('reminder_sent', models.BooleanField(default=False)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_tasks', to='businesses.business')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='crm.crmcontact')),
                ('deal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='crm.crmdeal')),
            ],
            options={
                'verbose_name': 'CRM Task',
                'verbose_name_plural': 'CRM Tasks',
                'ordering': ['due_date', '-created_at'],
            },
        ),
    ]
