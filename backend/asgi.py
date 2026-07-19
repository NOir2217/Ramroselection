"""
ASGI config for ramroselection project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    raise KeyError(
        "The DJANGO_SETTINGS_MODULE environment variable is not set. "
        "It must be explicitly defined in production (e.g. backend.settings.production)."
    )

application = get_asgi_application()
