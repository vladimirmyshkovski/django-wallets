from django.db import models


class ApiKeyManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        objects = [obj.id for obj in queryset if not obj.is_expire]
        return queryset.filter(id__in=objects).values_list('api_key', flat=True)
