from django.contrib import admin

from errormon.models import ExceptionModel

class ExceptionModelAdmin(admin.ModelAdmin):
    list_display = ( "id", "occurred_at", "status_code", "exc_type", "exc_value" )
    ordering = ("-occurred_at",)
    search_felds = ( "exc_type", "exc_value", "exc_traceback", "req_path" )

admin.site.register(ExceptionModel, ExceptionModelAdmin)
