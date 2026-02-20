import pytest
from django.test import RequestFactory, override_settings

from src.accounts.enums import LeaseLevel
from src.accounts.middleware import TenantResolutionMiddleware
from src.processes.tests.fixtures import create_test_account

pytestmark = pytest.mark.django_db


@override_settings(MULTITENANCY_ENABLED=True)
def test_tenant_resolution_middleware__custom_domain__ok():
    request = RequestFactory().get('/', HTTP_HOST='tenant.customer.com')
    account = create_test_account()
    account.custom_domain = 'tenant.customer.com'
    account.save(update_fields=['custom_domain'])

    middleware = TenantResolutionMiddleware(lambda req: req)

    middleware.process_request(request)

    assert request.tenant_account == account


@override_settings(MULTITENANCY_ENABLED=True, MULTITENANCY_BASE_DOMAIN='moworks.app')
def test_tenant_resolution_middleware__subdomain__ok():
    request = RequestFactory().get('/', HTTP_HOST='acme.moworks.app')
    account = create_test_account(lease_level=LeaseLevel.TENANT)
    account.tenant_slug = 'acme'
    account.save(update_fields=['tenant_slug'])

    middleware = TenantResolutionMiddleware(lambda req: req)

    middleware.process_request(request)

    assert request.tenant_account == account
    assert request.tenant_slug == 'acme'
