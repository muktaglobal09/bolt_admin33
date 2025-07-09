from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from colorfield.fields import ColorField
from apps.core.models import TimeStampedModel, SEOModel


class Category(MPTTModel, TimeStampedModel, SEOModel):
    """Hierarchical category model using MPTT."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    color = ColorField(default='#007bff', help_text="Category color for UI")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Business type specific fields
    is_service = models.BooleanField(default=True, help_text="Service-based businesses")
    is_product = models.BooleanField(default=False, help_text="Product-based businesses")
    is_manufacturing = models.BooleanField(default=False, help_text="Manufacturing businesses")
    is_freelancer = models.BooleanField(default=False, help_text="Freelancer/Professional services")
    
    class MPTTMeta:
        order_insertion_by = ['sort_order', 'name']
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def business_count(self):
        """Count of businesses in this category and its children."""
        from apps.businesses.models import Business
        return Business.objects.filter(category__in=self.get_descendants(include_self=True)).count()


class CategoryAttribute(TimeStampedModel):
    """Attributes specific to categories for filtering."""
    
    ATTRIBUTE_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('choice', 'Choice'),
        ('multi_choice', 'Multiple Choice'),
        ('range', 'Range'),
    )
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES)
    is_required = models.BooleanField(default=False)
    is_filterable = models.BooleanField(default=True)
    help_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Category Attribute'
        verbose_name_plural = 'Category Attributes'
        ordering = ['sort_order', 'name']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class CategoryAttributeOption(TimeStampedModel):
    """Options for choice-type category attributes."""
    attribute = models.ForeignKey(CategoryAttribute, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Category Attribute Option'
        verbose_name_plural = 'Category Attribute Options'
        ordering = ['sort_order', 'display_name']
        unique_together = ['attribute', 'value']
    
    def __str__(self):
        return f"{self.attribute.name} - {self.display_name}"


class Tag(TimeStampedModel):
    """Tags for additional categorization."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = ColorField(default='#6c757d')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name