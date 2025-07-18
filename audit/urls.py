from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditQueryViewSet
from .views import AuditQueryHistoryView


router = DefaultRouter()
router.register(r'auditqueries', AuditQueryViewSet, basename='auditquery')

urlpatterns = [
    path("api/query/<int:pk>/history/", AuditQueryHistoryView.as_view()),
       path('', include(router.urls)),
]
