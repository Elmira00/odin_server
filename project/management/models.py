from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from scraper.models import NewsArticle, Source


class Action(models.Model):
    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('status_change', 'Status Change'),
        ('delete', 'Delete'),
        ('comment', 'Comment'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True, related_name='actions')
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    is_deleted=models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user} - {self.action_type} at {self.timestamp}"

    class Meta:
        verbose_name = "User Action"
        verbose_name_plural = "User Actions"
        ordering = ['-timestamp']
        

class Category(models.Model):
    category = models.CharField(max_length=50)
    is_deleted=models.BooleanField(default=False)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['category']


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.comment[:30]}"

    class Meta:
        ordering = ['-created_at']


class Problem(models.Model):
    source = models.ForeignKey(
        Source,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='problems'
    )
    problem_description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted=models.BooleanField(default=False)
    is_sent=models.BooleanField(default=False)

    def __str__(self):
        return f"Problem in {self.source.name} - {self.category.category}"

    class Meta:
        ordering = ['-created_at']





class Task(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('review', 'Review'),
        ('completed', 'Completed'),
        ('archived',"Archived")
    ]
    problem = models.ForeignKey(
        Problem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_tasks', 
        null=True,
        blank=True
    )

    assigned_to = models.ManyToManyField(
        User,
        blank=True,
        related_name='assigned_tasks'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Select category if no problem is linked"
    )
    content = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted=models.BooleanField(default=False)
    def clean(self):
        if not self.problem and not self.category:
            raise ValidationError("You must either link a problem or select a category manually.")

        if self.problem and self.category:
            raise ValidationError("Cannot set category manually if problem is linked.")

    @property
    def effective_category(self):
        if self.problem:
            return self.problem.category
        return self.category

    def __str__(self):
        if self.problem_id:
            return f"Task (Problem ID: {self.problem_id})"
        return f"Task (Manual - {self.category})"

    class Meta:
        ordering = ['-created_at']


class SourceRule(models.Model):
    RESOLUTION_TYPES = [
        ('css_selector', 'CSS Selector'),
        ('meta', 'Meta Tag'),
        ('json_ld', 'JSON-LD'),
        ('api_json', 'API JSON'),
        ('url_regex', 'URL Regex'),
    ]

    problem = models.ForeignKey(
        Problem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_rules'
    )
    resolution_type = models.CharField(
        max_length=30,
        choices=RESOLUTION_TYPES,
        default='css_selector'
    )
    rule_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        source_name = self.problem.source.name if self.problem and self.problem.source else "Unknown Source"
        return f"Rule for {source_name} ({self.resolution_type})"

    class Meta:
        verbose_name = "Source Extraction Rule"
        verbose_name_plural = "Source Extraction Rules"
        ordering = ['-created_at']


class AutoHealerFinding(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'),
    ]

    source = models.ForeignKey(
        Source, 
        on_delete=models.CASCADE, 
        related_name='auto_healer_findings'
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )
    
    resolution_type = models.CharField(
        max_length=30, 
        choices=SourceRule.RESOLUTION_TYPES
    )
    rule_content = models.TextField()
    
    # Informational / Evidence fields for the UI
    confidence = models.FloatField(default=0.0)
    evidence_urls = models.TextField(
        blank=True, 
        null=True, 
        help_text="JSON list of sample URLs that generated this finding."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Auto Healer Finding"
        verbose_name_plural = "Auto Healer Findings"
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'category', 'resolution_type', 'rule_content'],
                name='unique_finding_candidate'
            )
        ]

    def __str__(self):
        source_name = self.source.name if self.source else "Unknown"
        return f"[{self.status}] {self.resolution_type} for {source_name} ({self.category.category})"