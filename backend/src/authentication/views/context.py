from django.contrib.auth import get_user_model
from rest_framework.generics import (
    ListAPIView,
)

from src.authentication.serializers import (
    ContextUserSerializer,
)
from src.generics.mixins.views import (
    BaseResponseMixin,
)
from src.generics.permissions import (
    IsAuthenticated,
)

UserModel = get_user_model()


class ContextUserView(
    ListAPIView,
    BaseResponseMixin,
):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = ContextUserSerializer(
            request.user,
            context={'is_supermode': request.is_superuser},
        ).data
        tenant_account = getattr(request, 'tenant_account', None)
        data['tenant_context'] = {
            'id': tenant_account.id,
            'name': tenant_account.name,
            'tenant_name': tenant_account.tenant_name,
            'tenant_slug': tenant_account.tenant_slug,
            'custom_domain': tenant_account.custom_domain,
        } if tenant_account else None
        return self.response_ok(data)
