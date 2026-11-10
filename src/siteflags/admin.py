from django.contrib import admin

from .utils import get_flag_model

FLAG_MODEL = get_flag_model()


@admin.register(FLAG_MODEL)
class FlagModelAdmin(admin.ModelAdmin):

    list_display = (
        'time_created',
        'content_type',
        'object_id',
        'status',
    )

    search_fields = (
        'object_id',
        'content_type',
        'user',
    )

    list_filter = (
        'time_created',
        'status',
        'content_type',
    )

    ordering = (
        '-time_created',
    )

    date_hierarchy = 'time_created'
