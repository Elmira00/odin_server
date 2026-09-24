
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task

@shared_task
def send_keyword_match_email(email, keyword, article_link):
    subject = f"Yeni məqalə: '{keyword}' açar sözünə uyğun xəbər tapıldı"
    message = f"Aşağıdakı linkdə '{keyword}' açar sözünə uyğun bir xəbər yerləşdirilib:\n\n{article_link}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)