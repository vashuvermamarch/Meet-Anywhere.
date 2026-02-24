import jwt
import time
import os
from django.conf import settings

def generate_jitsi_jwt(user, room_name, is_host):
    """
    Production-grade JWT for self-hosted Jitsi (HS256).
    Ensures moderator status is granted via cryptographically signed claims.
    """
    app_id = getattr(settings, 'JITSI_APP_ID', 'my_django_app')
    app_secret = getattr(settings, 'JITSI_APP_SECRET', None)
    jitsi_domain = getattr(settings, 'JITSI_DOMAIN', 'meet.jit.si')

    if not app_secret:
        return None

    # Expiry = 2 hours
    exp = int(time.time()) + (2 * 3600)

    payload = {
        "aud": "jitsi",
        "iss": app_id,
        "sub": jitsi_domain,
        "room": room_name,
        "room_name": room_name,
        "exp": exp,
        "context": {
            "user": {
                "name": user.username,
                "email": user.email,
                "moderator": is_host,
                "role": "moderator" if is_host else "participant"
            },
            "features": {
                "recording": is_host,
                "livestreaming": is_host,
                "screen-sharing": True
            }
        }
    }

    return jwt.encode(payload, app_secret, algorithm="HS256")
