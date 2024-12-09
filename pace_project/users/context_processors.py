from django.conf import settings
from django.core.cache import cache


def allauth_settings(request):
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }


def user_avatar_context(request):
    """
    Returns the user's avatar URL for authenticated users to be used across templates.
    If the user is not authenticated, returns an empty dictionary.
    """
    if request.user.is_authenticated:
        return {'user_avatar_url': get_cached_user_avatar_url(request.user)}
    return {}


def get_cached_user_avatar_url(user):
    """
    Retrieves the user's avatar URL from the cache, or generates and caches it if not already present.
    Caches the avatar URL for 24 hours (86400 seconds).
    """
    cache_key = f"user_avatar_{user.id}"
    avatar_url = cache.get(cache_key)

    if not avatar_url:
        avatar_url = user.get_avatar_url  # this method fetches the avatar URL
        if avatar_url:
            cache.set(cache_key, avatar_url, timeout=86400)  # Cache the avatar URL for 24 hours
        else:
            return None  # Return None if no avatar is set
    return avatar_url
