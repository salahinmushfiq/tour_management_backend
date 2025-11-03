from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, email):
    try:
        sent = send_mail(
            subject="Welcome to TourMate!",
            message="Thank you for joining TourMate! We’re excited to have you onboard.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        if sent == 1:
            return f"✅ Welcome email successfully sent to {email}"
        else:
            raise Exception("SMTP send_mail returned 0 (not sent)")
    except Exception as e:
        self.retry(exc=e, countdown=10)
        return f"❌ Failed to send email to {email}: {str(e)}"
