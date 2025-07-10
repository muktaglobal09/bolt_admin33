from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from colorfield.fields import ColorField
from apps.core.models import TimeStampedModel, SEOModel


class Category(MPTTModel, TimeStampedModel, SEOModel):
    """Hierarchical category model using MPTT."""
    
    name = models.CharField(max_length=100, unique=True, help_text="Category name (must be unique)")
    description = models.TextField(blank=True, help_text="Detailed description of the category")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', help_text="Parent category (leave empty for top-level category)")
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class for icon (e.g., 'fas fa-home', 'lucide-home')")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, help_text="Category image for visual representation")
    color = ColorField(default='#007bff', help_text="Category color for UI elements and branding")
    is_active = models.BooleanField(default=True, help_text="Whether this category is active and visible")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order for displaying categories (lower numbers appear first)")
    
    # Business type specific fields
    is_service = models.BooleanField(default=True, help_text="Allow service-based businesses in this category")
    is_product = models.BooleanField(default=False, help_text="Allow product-based businesses in this category")
    is_manufacturing = models.BooleanField(default=False, help_text="Allow manufacturing businesses in this category")
    is_freelancer = models.BooleanField(default=False, help_text="Allow freelancer/professional services in this category")
    
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
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attributes', help_text="Category this attribute belongs to")
    name = models.CharField(max_length=100, help_text="Attribute name (e.g., 'Price Range', 'Experience Level')")
    attribute_type = models.CharField(max_length=20, choices=ATTRIBUTE_TYPES, help_text="Type of attribute for input validation")
    is_required = models.BooleanField(default=False, help_text="Whether this attribute is required when creating a business")
    is_filterable = models.BooleanField(default=True, help_text="Whether users can filter by this attribute")
    help_text = models.CharField(max_length=255, blank=True, help_text="Help text shown to users when filling this attribute")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order for displaying attributes")
    
    class Meta:
        verbose_name = 'Category Attribute'
        verbose_name_plural = 'Category Attributes'
        ordering = ['sort_order', 'name']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class CategoryAttributeOption(TimeStampedModel):
    """Options for choice-type category attributes."""
    attribute = models.ForeignKey(CategoryAttribute, on_delete=models.CASCADE, related_name='options', help_text="Attribute this option belongs to")
    value = models.CharField(max_length=100, help_text="Internal value stored in database")
    display_name = models.CharField(max_length=100, help_text="User-friendly name displayed in forms")
    sort_order = models.PositiveIntegerField(default=0, help_text="Order for displaying options")
    
    class Meta:
        verbose_name = 'Category Attribute Option'
        verbose_name_plural = 'Category Attribute Options'
        ordering = ['sort_order', 'display_name']
        unique_together = ['attribute', 'value']
    
    def __str__(self):
        return f"{self.attribute.name} - {self.display_name}"


class Tag(TimeStampedModel):
    """Tags for additional categorization."""
    name = models.CharField(max_length=50, unique=True, help_text="Tag name (must be unique)")
    slug = models.SlugField(max_length=50, unique=True, help_text="URL-friendly version of the tag name")
    description = models.TextField(blank=True, help_text="Description of what this tag represents")
    color = ColorField(default='#6c757d', help_text="Color for displaying this tag")
    is_active = models.BooleanField(default=True, help_text="Whether this tag is active and can be used")
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name