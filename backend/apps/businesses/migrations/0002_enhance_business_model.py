# Generated by Django 4.2.7 on 2025-01-07 12:00

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('businesses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='conversion_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='business',
            name='health_status',
            field=models.CharField(choices=[('excellent', 'Excellent'), ('good', 'Good'), ('average', 'Average'), ('poor', 'Poor'), ('critical', 'Critical')], default='average', max_length=20),
        ),
        migrations.AddField(
            model_name='business',
            name='last_activity_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='business',
            name='lead_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='business',
            name='profile_completeness',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='business',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_businesses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='businessimage',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='businessproduct',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='businessproduct',
            name='sku',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='businessproduct',
            name='stock_quantity',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='businessservice',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='businessdocument',
            name='verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='businessdocument',
            name='verified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_documents', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BusinessAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('page_views', models.PositiveIntegerField(default=0)),
                ('unique_visitors', models.PositiveIntegerField(default=0)),
                ('inquiries', models.PositiveIntegerField(default=0)),
                ('leads', models.PositiveIntegerField(default=0)),
                ('conversions', models.PositiveIntegerField(default=0)),
                ('new_reviews', models.PositiveIntegerField(default=0)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('phone_clicks', models.PositiveIntegerField(default=0)),
                ('email_clicks', models.PositiveIntegerField(default=0)),
                ('website_clicks', models.PositiveIntegerField(default=0)),
                ('social_media_clicks', models.PositiveIntegerField(default=0)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='businesses.business')),
            ],
            options={
                'verbose_name': 'Business Analytics',
                'verbose_name_plural': 'Business Analytics',
                'ordering': ['-date'],
                'unique_together': {('business', 'date')},
            },
        ),
        migrations.CreateModel(
            name='BusinessVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('verification_type', models.CharField(choices=[('document', 'Document Verification'), ('phone', 'Phone Verification'), ('email', 'Email Verification'), ('address', 'Address Verification'), ('manual', 'Manual Verification')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True)),
                ('rejection_reason', models.TextField(blank=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verifications', to='businesses.business')),
                ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='business_verifications', to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                'verbose_name': 'Business Verification',
                'verbose_name_plural': 'Business Verifications',
                'ordering': ['-created_at'],
                'unique_together': {('business', 'verification_type')},
            },
        ),
        migrations.CreateModel(
            name='BusinessSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('auto_renew', models.BooleanField(default=True)),
                ('used_listings', models.PositiveIntegerField(default=0)),
                ('used_images', models.PositiveIntegerField(default=0)),
                ('used_services', models.PositiveIntegerField(default=0)),
                ('used_products', models.PositiveIntegerField(default=0)),
                ('used_lead_credits', models.PositiveIntegerField(default=0)),
                ('business', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='businesses.business')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payments.subscriptionplan')),
            ],
            options={
                'verbose_name': 'Business Subscription',
                'verbose_name_plural': 'Business Subscriptions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='business',
            index=models.Index(fields=['verification_status'], name='businesses_b_verific_8b5c8a_idx'),
        ),
        migrations.AddIndex(
            model_name='business',
            index=models.Index(fields=['is_featured'], name='businesses_b_is_feat_c8b9a1_idx'),
        ),
        migrations.AddIndex(
            model_name='business',
            index=models.Index(fields=['health_status'], name='businesses_b_health__2f4d5e_idx'),
        ),
        migrations.AddIndex(
            model_name='business',
            index=models.Index(fields=['category'], name='businesses_b_categor_7a8b9c_idx'),
        ),
        migrations.AddIndex(
            model_name='business',
            index=models.Index(fields=['owner'], name='businesses_b_owner_i_1d2e3f_idx'),
        ),
        migrations.AddIndex(
            model_name='businessanalytics',
            index=models.Index(fields=['business', 'date'], name='businesses_b_busines_4g5h6i_idx'),
        ),
    ]