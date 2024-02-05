import logging

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.db import models


log = logging.getLogger(__name__)

if settings.DEBUG:

    class AdminDebugMixin(admin.ModelAdmin):
        def get_autocomplete_fields(self, request):
            """add autocomplete_fields automatically"""

            fields = super().get_autocomplete_fields(request)
            for field in self.model._meta.fields:
                if field.is_relation and field.related_model:
                    fields += (field.name,)
            for field in self.model._meta.many_to_many:
                fields += (field.name,)
            return fields

        def get_search_fields(self, request):
            """add search_fields automatically"""

            fields = super().get_search_fields(request)
            for field in self.model._meta.fields:
                if field.primary_key or isinstance(field, models.CharField):
                    fields += (field.name,)
            return fields

        def get_list_display(self, request):
            """add list_displays automatically"""

            fields = []
            for field in self.model._meta.fields:
                if not field.editable:
                    continue
                if field.primary_key:
                    fields.insert(0, field.name)
                    continue
                fields.append(field.name)
            return fields

        def get_list_filter(self, request):
            """add list_filter automatically"""

            fields = super().get_list_filter(request)
            for field in self.model._meta.fields:
                if field.choices and len(field.choices) < 10:
                    fields += (field.name,)
            return fields

    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            try:

                @admin.register(model)
                class ModelAdmin(AdminDebugMixin):
                    pass

            except admin.sites.AlreadyRegistered:
                pass
