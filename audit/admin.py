from django.contrib import admin
from .models import AuditQuery
from .models import Profile
from simple_history.admin import SimpleHistoryAdmin


from .signals import set_current_user
# Register your models here.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)


@admin.register(AuditQuery)
# class AuditQueryAdmin(admin.ModelAdmin):this is old
class AuditQueryAdmin(SimpleHistoryAdmin): 
    list_display = (
        'id',
        'query_type',
        'auditee_action_owner',
        'auditee_status',
        'auditor_status',
        'updated_by',
        'updated_time'
    )
    list_filter = ('query_type', 'auditee_status', 'auditor_status')
    search_fields = ('auditee_action_owner', 'remarks', 'updated_by')
    ordering = ('-updated_time',)

    readonly_fields = ('auditee_status',)


    def auditee_status_display(self, obj):
        return obj.auditee_status or "-"
    auditee_status_display.short_description = "Auditee Status"

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []  # ✅ Superadmin: full access

        role = getattr(request.user.profile, 'role', None)

        if role == 'Auditee':
            # ✅ Auditee can only edit 'auditee_status'and remarks
               return [f.name for f in self.model._meta.fields if f.name not in ['auditee_status', 'remarks']]
        if role == 'Auditor':
            # ❌ Auditor cannot edit 'auditee_status'
            return ['auditee_status']

        return []

    def has_add_permission(self, request):
        return True if request.user.is_superuser else (
            hasattr(request.user, 'profile') and request.user.profile.role != 'Auditee'
        )

    def has_delete_permission(self, request, obj=None):
        return True if request.user.is_superuser else (
            hasattr(request.user, 'profile') and request.user.profile.role != 'Auditee'
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'profile') and request.user.profile.role == 'Auditee':
            return qs.filter(auditee_action_owner=request.user.username)
        return qs

    
    def save_model(self, request, obj, form, change):
        set_current_user(request.user)
        super().save_model(request, obj, form, change)  


