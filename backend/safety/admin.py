from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CampusArea, InspectionPoint, InspectionRecord, HazardReport, RectifyTask, RectifyRecord, SystemLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'phone', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'phone']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('其他信息', {'fields': ('role', 'phone', 'avatar')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('其他信息', {'fields': ('role', 'phone')}),
    )


@admin.register(CampusArea)
class CampusAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'area_type', 'parent', 'is_active']
    list_filter = ['area_type', 'is_active']
    search_fields = ['name', 'code']


@admin.register(InspectionPoint)
class InspectionPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'area', 'inspection_frequency', 'is_active']
    list_filter = ['inspection_frequency', 'is_active', 'area']
    search_fields = ['name', 'code', 'location']
    filter_horizontal = ['responsible_users']


@admin.register(InspectionRecord)
class InspectionRecordAdmin(admin.ModelAdmin):
    list_display = ['point', 'inspector', 'status', 'inspection_time']
    list_filter = ['status', 'inspection_time']
    search_fields = ['point__name', 'inspector__username']
    readonly_fields = ['created_at']


@admin.register(HazardReport)
class HazardReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'hazard_type', 'level', 'status', 'reporter', 'created_at']
    list_filter = ['status', 'hazard_type', 'level']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RectifyTask)
class RectifyTaskAdmin(admin.ModelAdmin):
    list_display = ['hazard', 'assignee', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'deadline']
    search_fields = ['hazard__title', 'assignee__username']


@admin.register(RectifyRecord)
class RectifyRecordAdmin(admin.ModelAdmin):
    list_display = ['task', 'result', 'reviewer', 'reviewed_at']
    list_filter = ['result', 'reviewed_at']
    search_fields = ['task__hazard__title']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'ip_address', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']