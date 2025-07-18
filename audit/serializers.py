from rest_framework import serializers
from .models import AuditQuery

from rest_framework import serializers


class AuditQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditQuery
        fields = '__all__'
    
    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        user = request.user if request else None

        # ✅ If superuser, allow all fields editable
        if user and user.is_superuser:
            return fields

        # ✅ If user has a profile and a role
        if hasattr(user, 'profile'):
            role = user.profile.role

            if role == 'Auditee':
                # Auditee: only 'auditee_status' is editable
                for field_name in fields:
                    if field_name != 'auditee_status':
                        fields[field_name].read_only = True

            elif role == 'Auditor':
                # Auditor: 'auditee_status' is read-only
                fields['auditee_status'].read_only = True

        return fields
    
    
    def get_readonly_fields(self, request, obj=None):
        # ✅ Superadmin can edit everything
        if request.user.is_superuser:
            return []

        role = getattr(request.user.profile, 'role', None)

        if role == 'Auditee':
            # ✅ Auditee: only 'auditee_status' is editable
            return [f.name for f in self.model._meta.fields if f.name != 'auditee_status']

        if role == 'Auditor':
            # ✅ Auditor: all except 'auditee_status'
            return ['auditee_status']

        return super().get_readonly_fields(request, obj)
    

class AuditQueryHistorySerializer(serializers.Serializer):
    history_id = serializers.IntegerField()
    history_date = serializers.DateTimeField()
    history_user = serializers.CharField()
    changes = serializers.SerializerMethodField()

    def get_changes(self, obj):
        try:
            prev = obj.prev_record
            changes = {}
            for field in obj.instance._meta.fields:
                field_name = field.name
                old = getattr(prev, field_name, None)
                new = getattr(obj, field_name, None)
                if old != new:
                    changes[field_name] = {
                        "from": old,
                        "to": new
                    }
            return changes
        except Exception:
            return {}