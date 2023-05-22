from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import New

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives

@receiver(post_save, sender=New)
def product_created(instance, created, **kwargs):
    emails = User.objects.filter(
        subscriptions__category=instance.category
    ).values_list('email', flat=True)

    subject = f'Новая новость в категории {instance.category}'

    text_content = (
        f'Название: {instance.title}\n'
        f'Анонс: {instance.full_text}\n\n'
        f'Ссылка на публикацию: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )

    html_content = (
        f'Название: {instance.title}<br>'
        f'Анонс: {instance.full_text}<br><br>'
        f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
        f'Ссылка на публикацию</a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
