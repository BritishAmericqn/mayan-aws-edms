from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .models import SharedDocument


@admin.register(SharedDocument)
class SharedDocumentAdmin(admin.ModelAdmin):
    """
    Simplified Django admin interface for SharedDocument model.
    Basic version for debugging - will enhance after confirming it works.
    """
    
    list_display = (
        'label',
        'document',
        'created_by',
        'created_at',
        'is_active',
    )
    
    list_filter = (
        'is_active',
        'created_at',
        'expires_at',
    )
    
    search_fields = (
        'label',
        'document__label',
        'created_by__username',
    )
    
    readonly_fields = (
        'url_key',
        'created_at',
        'access_count',
        'last_accessed_at',
        'last_accessed_from_ip',
    )
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'label',
                'document',
                'created_by',
                'is_active',
            )
        }),
        (_('Expiration Settings'), {
            'fields': (
                'expires_at',
                'max_access_count',
            )
        }),
        (_('System Information'), {
            'fields': (
                'url_key',
                'created_at',
                'access_count',
                'last_accessed_at',
                'last_accessed_from_ip',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related object fetching."""
        return super().get_queryset(request).select_related(
            'document',
            'created_by'
        ) 