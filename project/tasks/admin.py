from django.contrib import admin
from .models import KeywordsNewsArticleCombination,TempDataEmail,TempDataTelegram,TelegramUser

class KeywordsNewsArticleCombinationAdmin(admin.ModelAdmin):
    list_display = ('keyword_id', 'user_id','newsarticle_id', 'created_at')
    autocomplete_fields = ['newsarticle_id']
    

class TempDataEmailAdmin(admin.ModelAdmin):
    list_display = ('user_id','is_send','created_at')

class TempDataTelegramAdmin(admin.ModelAdmin):
    list_display = ('user_id','is_send','created_at')
    
    
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username','chat_id', 'created_at')
    search_fields = ('user_id', 'username')

admin.site.register(KeywordsNewsArticleCombination, KeywordsNewsArticleCombinationAdmin)
admin.site.register(TempDataEmail, TempDataEmailAdmin)
admin.site.register(TempDataTelegram, TempDataTelegramAdmin)
admin.site.register(TelegramUser)




