from django.contrib import admin
from .models import Confession, ConfessionTag, ConfessionCategory


# Register Django models in Django admin
class ConfessionAdmin(admin.ModelAdmin):
    list_display = ['generated_title', 'pseudo', 'tone', 'is_public', 'is_internal', 'created_at']
    list_filter = ['tone', 'is_public', 'is_internal', 'created_at']
    search_fields = ['text', 'pseudo', 'generated_title']
    filter_horizontal = ['tags']


class ConfessionTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']


admin.site.register(Confession, ConfessionAdmin)
admin.site.register(ConfessionTag, ConfessionTagAdmin)