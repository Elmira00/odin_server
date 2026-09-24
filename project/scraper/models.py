from django.db import models
from utils.photo_save import logo_dir_wrapper
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.core.files.storage import FileSystemStorage
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError




class UniqueImageStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        return name 

    def save(self, name, content, max_length=None):
        if self.exists(name):
            return name
        return super().save(name, content, max_length=max_length)


class Region(models.Model):
    name = models.CharField(max_length=100,verbose_name='Name')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.id} - {self.name}'
    
    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
    
    
class Source(models.Model):
    name = models.CharField(max_length=100,verbose_name='Full Site Name',null=True,blank=True)
    region_id = models.ForeignKey(Region, on_delete=models.SET_NULL,null=True,
                                  verbose_name='Region',related_name='sources')
    link = models.CharField(max_length=255,verbose_name='Site Link',null=True,blank=True,unique=True)
    rss_link = models.CharField(max_length=255,verbose_name='RSS Link',null=True,blank=True,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(null=True,blank=True,verbose_name='Type')
    is_active = models.BooleanField(default=True,verbose_name='Is Active')

    def __str__(self):
        return f'{self.id} - {self.name}'
    
    class Meta:
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'
        
        
class NewsArticle(models.Model):
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True,verbose_name='Source',related_name='newsarticles')
    url = models.URLField(max_length=2048,unique=True)
    title = models.CharField(max_length=1500,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    news_shared_date = models.DateTimeField( null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return f'{self.id} - {self.url}'  
    
    
    class Meta:
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
        
        
class ChangedNewsArticle(models.Model):
    newsarticle = models.ForeignKey(NewsArticle, on_delete=models.CASCADE,related_name='changednewsarticles')
    title = models.CharField(max_length=1500,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    news_shared_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def source(self):
        return self.newsarticle.source if self.newsarticle and self.newsarticle.source else None
    
    def __str__(self):
        if self.title:
            return self.title
        else:
            return f'{self.id} - {self.newsarticle.url}'
    
    class Meta:
        verbose_name = 'Changed News Article'
        verbose_name_plural = 'Changed News Articles'
        
        
        

def news_image_path(instance, filename):
    
    from datetime import datetime
    dt = datetime.now()
    base_folder = 'main' if instance.is_main else 'gallery'
    source_id = instance.newsarticle.source.id if instance.newsarticle else 0
    return f"{base_folder}/{source_id}/{dt.year}/{dt.month:02d}/{dt.day:02d}/{filename}"



class NewsImage(models.Model):
    newsarticle = models.ForeignKey('NewsArticle',on_delete=models.CASCADE,related_name='images',null=True,blank=True)
    changed_newsarticle = models.ForeignKey('ChangedNewsArticle',on_delete=models.CASCADE,related_name='images',null=True,blank=True)
    image_url = models.URLField(max_length=2048,null=True, blank=True)
    base64_image = models.TextField(null=True, blank=True)
    local_image_url = models.ImageField(upload_to=news_image_path, null=True, blank=True,max_length=2048)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.newsarticle:
            return f"Image for NewsArticle {self.newsarticle_id} ({'Main' if self.is_main else 'Gallery'})"
        elif self.changed_newsarticle:
            return f"Image for ChangedArticle {self.changed_newsarticle_id} ({'Main' if self.is_main else 'Gallery'})"
        return "Unlinked Image"

    class Meta:
        verbose_name = 'News Image'
        verbose_name_plural = 'News Images'


class SearchWords(models.Model):
    word = models.CharField(max_length=200,verbose_name="Search Word")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.id} - {self.word}'
    
    class Meta:
        verbose_name = 'Search Word'
        verbose_name_plural = 'Search Words'
        
        
class Exclude(models.Model):
    FIELD_CHOICES = [
        ('title', 'Title'),
        ('description', 'Description'),
        ('content', 'Content'),
        ('news_shared_date', 'News Shared Date'),
        ('image', 'Image'),
    ]
    source = models.ForeignKey(
        'Source',
        on_delete=models.CASCADE,
        related_name='excludes',
        verbose_name='Source'
    )
    fields = MultiSelectField(
        choices=FIELD_CHOICES,
        verbose_name='Fields to Exclude',
        null=True,
        max_length=150
    )

    def __str__(self):
        return f"Exclude {self.get_fields_display()} for Source: {self.source.name}"

    class Meta:
        verbose_name = 'Exclude'
        verbose_name_plural = 'Excludes'

        constraints = [
            models.UniqueConstraint(
                fields=['source'],
                name='unique_exclude_per_source'
            )
        ]

