"""Custom storage backends for Cloudflare R2 (S3-compatible).

The project's default media storage (``STORAGES["default"]`` in
``settings/production.py``) points at a **public** R2 bucket served through a
custom domain — used for marketing media (project photos, testimonials).

Sensitive lead uploads (electricity bills, meter/roof photos) must NOT be
publicly reachable, so they live in a separate **private** bucket and are served
via short-lived signed URLs. ``PrivateMediaStorage`` below provides that, and
``private_media_storage`` selects it only when a private bucket is configured —
otherwise it falls back to the project default (local filesystem in dev/tests),
so development and CI don't need R2 credentials.
"""

from __future__ import annotations

from django.conf import settings
from django.core.files.storage import default_storage
from storages.backends.s3 import S3Storage


class PrivateMediaStorage(S3Storage):
    """Private R2 bucket with signed, expiring URLs (no public/custom domain).

    Inherits the R2 endpoint / signature / addressing settings from the global
    ``AWS_S3_*`` settings; only the bucket, ACL and URL-signing behaviour differ
    from the default public store.
    """

    location = "leads"
    default_acl = None  # R2 has no ACLs
    file_overwrite = False
    querystring_auth = True  # serve via signed, expiring URLs
    custom_domain = None  # never use the public CDN domain for private files

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        private_bucket = getattr(settings, "AWS_PRIVATE_STORAGE_BUCKET_NAME", "")
        if private_bucket:
            self.bucket_name = private_bucket


def private_media_storage():
    """Storage selector for sensitive lead-upload FileFields.

    Returns the private R2 bucket when one is configured (production), else the
    project default storage so local dev / tests work without R2. Referenced by
    its import path in migrations, so keep this name/location stable.
    """
    if getattr(settings, "AWS_PRIVATE_STORAGE_BUCKET_NAME", ""):
        return PrivateMediaStorage()
    return default_storage
