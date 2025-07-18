from rest_framework import viewsets
from .models import AuditQuery
from .signals import set_current_user
from rest_framework.response import Response
from .serializers import AuditQuerySerializer
from .models import AuditQuery

from simple_history.utils import update_change_reason
from rest_framework.decorators import api_view
from rest_framework.response import Response


from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AuditQueryHistorySerializer



@api_view(['GET'])
def audit_query_history(request, pk):
    try:
        query = AuditQuery.objects.get(pk=pk)
    except AuditQuery.DoesNotExist:
        return Response({'error': 'Query not found'}, status=404)

    history = query.history.all().order_by('-history_date')
    result = []

    for i in range(1, len(history)):
        newer = history[i - 1]
        older = history[i]
        changes = newer.diff_against(older)
        change_list = []
        for change in changes.changes:
            change_list.append(f"{change.field}: {change.old} → {change.new}")
        result.append({
            "changed_at": newer.history_date.strftime("%b %d, %Y %I:%M %p"),
            "changed_by": newer.history_user.username if newer.history_user else "Unknown",
            "changes": change_list
        })

    return Response(result)

class AuditQueryViewSet(viewsets.ModelViewSet):
    queryset = AuditQuery.objects.all().order_by('-updated_time')
    serializer_class = AuditQuerySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if hasattr(user, 'profile') and user.profile.role == 'Auditee':
            return self.queryset.filter(auditee_action_owner=user.username)
        return self.queryset

    def perform_update(self, serializer):
        print("set_current_user called:", self.request.user)
        set_current_user(self.request.user)    # ✅ This ensures logging works
        return super().perform_update(serializer)
    
    def perform_create(self, serializer):
        set_current_user(self.request.user)  # ✅ Optional: log creation too
        return super().perform_create(serializer)
    

class AuditQueryHistoryView(APIView):
    def get(self, request, pk):
        obj = AuditQuery.objects.get(pk=pk)
        history = obj.history.all().order_by("-history_date")
        serializer = AuditQueryHistorySerializer(history, many=True)
        return Response(serializer.data)
 
