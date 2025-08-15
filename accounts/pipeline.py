# accounts/pipeline.py
from accounts.models import User


def create_user_if_none(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    email = details.get('email')
    if not email:
        return

    user = User.objects.create(email=email)
    user.set_unusable_password()
    user.save()
    return {
        'is_new': True,
        'user': user
    }
