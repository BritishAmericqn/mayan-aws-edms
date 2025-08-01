from django.contrib import admin

from .models import (
    Workflow, WorkflowInstance, WorkflowInstanceLogEntry, WorkflowState,
    WorkflowStateAction, WorkflowTransition
)


class WorkflowInstanceLogEntryInline(admin.TabularInline):
    extra = 1
    model = WorkflowInstanceLogEntry


class WorkflowStateInline(admin.TabularInline):
    model = WorkflowState


class WorkflowTransitionInline(admin.TabularInline):
    model = WorkflowTransition


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    def document_types_list(self, instance):
        return ','.join(
            instance.document_types.values_list('label', flat=True)
        )

    filter_horizontal = ('document_types',)
    inlines = (WorkflowStateInline, WorkflowTransitionInline)
    list_display = (
        'label', 'internal_name', 'document_types_list', 'auto_launch',
        'ignore_completed'
    )


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    inlines = (WorkflowInstanceLogEntryInline,)
    list_display = (
        'workflow', 'document', 'state_active', 'get_last_transition'
    )


@admin.register(WorkflowStateAction)
class WorkflowStateActionAdmin(admin.ModelAdmin):
    list_display = (
        'state', 'label', 'enabled', 'when', 'backend_path', 'backend_data'
    )
