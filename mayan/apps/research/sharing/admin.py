from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import SharedDocument


@admin.register(SharedDocument)
class SharedDocumentAdmin(admin.ModelAdmin):
    """
    Enhanced Django admin interface for SharedDocument model with public URL display.
    """
    
    list_display = (
        'label',
        'document',
        'created_by',
        'created_at',
        'is_active',
        'public_url_short',
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
        'public_url_display',
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
        (_('Public Access'), {
            'fields': (
                'public_url_display',
            ),
            'description': 'Copy this URL to share the document with external users (no login required)',
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

    def public_url_display(self, obj):
        """Display the public-facing URL in a user-friendly format with copy functionality."""
        if obj.url_key:
            public_url = f"http://localhost/shared/{obj.url_key}/"
            
            # Create a styled, copyable URL display
            html = f'''
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="flex: 1;">
                        <div style="font-weight: bold; color: #198754; margin-bottom: 5px;">
                            <i class="fas fa-link"></i> Public Access URL
                        </div>
                        <div style="font-family: monospace; background: white; padding: 8px; border-radius: 4px; border: 1px solid #ccc; word-break: break-all;">
                            <a href="{public_url}" target="_blank" style="color: #0d6efd; text-decoration: none;">
                                {public_url}
                            </a>
                        </div>
                    </div>
                    <div>
                        <button type="button" onclick="navigator.clipboard.writeText('{public_url}').then(() => alert('URL copied to clipboard!'))" 
                                style="background: #0d6efd; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">
                            📋 Copy
                        </button>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <a href="{public_url}" target="_blank" style="color: #198754; text-decoration: none; font-weight: 500;">
                        🔗 Open in New Tab
                    </a>
                    <span style="margin: 0 10px;">|</span>
                    <a href="{public_url}download/" target="_blank" style="color: #ffc107; text-decoration: none; font-weight: 500;">
                        📥 Direct Download
                    </a>
                    <span style="margin: 0 10px;">|</span>
                    <a href="{public_url}preview/" target="_blank" style="color: #6f42c1; text-decoration: none; font-weight: 500;">
                        👁️ Preview
                    </a>
                </div>
            </div>
            '''
            return mark_safe(html)
        return _('URL not generated yet')
    
    public_url_display.short_description = _('Public Sharing URL')

    def public_url_short(self, obj):
        """Short URL display for list view."""
        if obj.url_key:
            return format_html(
                '<a href="http://localhost/shared/{}" target="_blank" style="color: #198754; font-weight: bold;">🔗 Public Link</a>',
                obj.url_key
            )
        return _('No URL')
    
    public_url_short.short_description = _('Public URL')

    def get_queryset(self, request):
        """Optimize queryset with related object fetching."""
        return super().get_queryset(request).select_related(
            'document',
            'created_by'
        ) 