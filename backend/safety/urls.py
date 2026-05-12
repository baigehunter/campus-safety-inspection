from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginViewSet, LogoutViewSet, UserViewSet, CampusAreaViewSet,
    InspectionPointViewSet, InspectionRecordViewSet,
    HazardReportViewSet, RectifyTaskViewSet,
    RectifyRecordViewSet, DashboardViewSet, SystemLogViewSet,
    FileUploadView, HazardAnalyzeView, InspectionAnalyzeView,
    NotificationViewSet, NotificationPreferenceViewSet, WeChatViewSet
)

router = DefaultRouter()
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'users', UserViewSet, basename='user')
router.register(r'areas', CampusAreaViewSet, basename='area')
router.register(r'points', InspectionPointViewSet, basename='point')
router.register(r'records', InspectionRecordViewSet, basename='record')
router.register(r'hazards', HazardReportViewSet, basename='hazard')
router.register(r'tasks', RectifyTaskViewSet, basename='task')
router.register(r'rectify-records', RectifyRecordViewSet, basename='rectify-record')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'logs', SystemLogViewSet, basename='log')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'wx', WeChatViewSet, basename='wx')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('upload/', FileUploadView.as_view(), name='file_upload'),
    path('analyze/', HazardAnalyzeView.as_view(), name='hazard_analyze'),
    path('analyze-inspection/', InspectionAnalyzeView.as_view(), name='inspection_analyze'),
]