from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from src.accounts.enums import LeaseLevel
from src.accounts.models import Account


class TenantResolutionMiddleware(MiddlewareMixin):
    """Resolve tenant account from request host for domain-based multitenancy."""

    def process_request(self, request):
        request.tenant_account = None
        request.tenant_slug = None

        if not settings.MULTITENANCY_ENABLED:
            return None

        host = request.get_host().split(':', 1)[0].lower()
        if host.startswith('www.'):
            host = host[4:]

        account = Account.objects.filter(custom_domain__iexact=host).first()
        if account:
            request.tenant_account = account
            request.tenant_slug = account.tenant_slug
            return None

        base_domain = settings.MULTITENANCY_BASE_DOMAIN.lower().lstrip('.')
        suffix = f'.{base_domain}'
        if not host.endswith(suffix):
            return None

        tenant_slug = host[:-len(suffix)]
        if not tenant_slug:
            return None

        account = Account.objects.filter(
            tenant_slug=tenant_slug,
            lease_level=LeaseLevel.TENANT,
        ).first()
        if account:
            request.tenant_account = account
            request.tenant_slug = tenant_slug

        return None
