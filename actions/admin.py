from django.contrib import admin

from .models import MediaAction, WatchState


@admin.register(MediaAction)
class MediaActionAdmin(admin.ModelAdmin):
    pass


@admin.register(WatchState)
class WatchStateAdmin(admin.ModelAdmin):
    pass
