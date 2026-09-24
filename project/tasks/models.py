from django.db import models
from scraper.models import NewsArticle

        
         
class KeywordsNewsArticleCombination(models.Model):
    keyword_id = models.IntegerField(verbose_name="Keywords id",null=True,blank=True)
    user_id = models.IntegerField(verbose_name="User id",null=True,blank=True)
    newsarticle_id = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, verbose_name="NewsArticle id",related_name='newsarticle_keywords')
    email_status = models.BooleanField(default=False, verbose_name="Email status")
    telegram_status = models.BooleanField(default=False, verbose_name="Telegram status")
    is_email_processed = models.BooleanField(default=False)
    is_telegram_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.keyword_id} -> {self.user_id}'
    
    class Meta:
        verbose_name = 'Keyword NewsArticle Combination'
        verbose_name_plural = 'Keyword NewsArticle Combinations'
        unique_together = ["user_id", "keyword_id", "newsarticle_id"]

        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["newsarticle_id"]),
            models.Index(fields=["keyword_id"]),
        ]
        
class TempDataEmail(models.Model):
    user_id = models.IntegerField(verbose_name="User id",null=True,blank=True)
    match_keyword_newsarticle = models.TextField(null=True,blank=True)
    keywords = models.TextField(null=True,blank=True)
    newsarticles = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_send = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user_id}'
    
    class Meta:
        verbose_name = 'Temp mail data'
        verbose_name_plural = 'Temp mail data'
        
        
class TempDataTelegram(models.Model):
    user_id = models.IntegerField(verbose_name="User id",null=True,blank=True)
    match_keyword_newsarticle = models.TextField(null=True,blank=True)
    keywords = models.TextField(null=True,blank=True)
    newsarticles = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_send = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f'{self.user_id}'
    
    class Meta:
        verbose_name = 'Temp telegram data'
        verbose_name_plural = 'Temp telegram data'
        
        
        

class TelegramUser(models.Model):
    user_id = models.IntegerField(unique=True, verbose_name="User id",null=True,blank=True)
    username = models.CharField(max_length=255,unique=True, verbose_name="Username",null=True,blank=True)
    chat_id = models.CharField(max_length=255,unique=True, verbose_name="Chat id",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    
    def __str__(self):
        return f'{self.user_id} - {self.username}'
