from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, CampusArea, InspectionPoint, InspectionRecord, HazardReport, RectifyTask, RectifyRecord, SystemLog, Notification, NotificationPreference


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    role_name = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'role_name', 'phone', 'avatar', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'role', 'phone']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')
        data['user'] = user
        return data


class CampusAreaSerializer(serializers.ModelSerializer):
    """校园区域序列化器"""
    area_type_name = serializers.CharField(source='get_area_type_display', read_only=True)
    children = serializers.SerializerMethodField()
    point_count = serializers.SerializerMethodField()

    class Meta:
        model = CampusArea
        fields = ['id', 'name', 'code', 'area_type', 'area_type_name', 'parent', 'children', 'description', 'is_active', 'point_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_children(self, obj):
        children = obj.children.all()
        return CampusAreaSerializer(children, many=True).data if children else []

    def get_point_count(self, obj):
        return obj.points.filter(is_active=True).count()


class InspectionPointSerializer(serializers.ModelSerializer):
    """巡检点位序列化器"""
    area_name = serializers.CharField(source='area.name', read_only=True)
    area_code = serializers.CharField(source='area.code', read_only=True)
    frequency_name = serializers.CharField(source='get_inspection_frequency_display', read_only=True)
    responsible_names = serializers.SerializerMethodField()

    class Meta:
        model = InspectionPoint
        fields = ['id', 'name', 'code', 'area', 'area_name', 'area_code', 'location', 'inspection_frequency', 'frequency_name', 'inspection_content', 'responsible_users', 'responsible_names', 'is_active', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_responsible_names(self, obj):
        return [user.username for user in obj.responsible_users.all()]


class InspectionRecordSerializer(serializers.ModelSerializer):
    """巡检记录序列化器"""
    point_name = serializers.CharField(source='point.name', read_only=True)
    inspector_name = serializers.CharField(source='inspector.username', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = InspectionRecord
        fields = ['id', 'point', 'point_name', 'inspector', 'inspector_name', 'status', 'status_name', 'inspection_photos', 'remark', 'inspection_time', 'created_at',
                  'ai_status', 'ai_tags', 'ai_analysis']
        read_only_fields = ['id', 'created_at']


class InspectionRecordCreateSerializer(serializers.ModelSerializer):
    """巡检记录创建序列化器"""

    class Meta:
        model = InspectionRecord
        fields = ['point', 'status', 'inspection_photos', 'remark', 'inspection_time',
                  'ai_status', 'ai_tags', 'ai_analysis']


class HazardReportSerializer(serializers.ModelSerializer):
    """安全隐患序列化器"""
    hazard_type_name = serializers.CharField(source='get_hazard_type_display', read_only=True)
    level_name = serializers.CharField(source='get_level_display', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    area_name = serializers.CharField(source='area.name', read_only=True)
    point_name = serializers.CharField(source='point.name', read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)

    class Meta:
        model = HazardReport
        fields = ['id', 'title', 'description', 'hazard_type', 'hazard_type_name',
                  'level', 'level_name', 'area', 'area_name', 'point', 'point_name',
                  'location', 'photos', 'reporter', 'reporter_name', 'status',
                  'status_name', 'deadline', 'created_at',
                  'ai_tags', 'ai_analysis', 'ai_hazard_type', 'ai_level']
        read_only_fields = ['id', 'created_at']


class HazardReportCreateSerializer(serializers.ModelSerializer):
    """安全隐患创建序列化器"""

    class Meta:
        model = HazardReport
        fields = ['title', 'description', 'hazard_type', 'level', 'area', 'point',
                  'location', 'photos', 'deadline',
                  'ai_tags', 'ai_analysis', 'ai_hazard_type', 'ai_level']


class RectifyTaskSerializer(serializers.ModelSerializer):
    """整改任务序列化器"""
    hazard_title = serializers.CharField(source='hazard.title', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    assigner_name = serializers.CharField(source='assigner.username', read_only=True)

    class Meta:
        model = RectifyTask
        fields = ['id', 'hazard', 'hazard_title', 'assignee', 'assignee_name', 'assigner', 'assigner_name', 'description', 'deadline', 'status', 'status_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class RectifyTaskCreateSerializer(serializers.ModelSerializer):
    """整改任务创建序列化器"""

    class Meta:
        model = RectifyTask
        fields = ['hazard', 'assignee', 'description', 'deadline']


class RectifyRecordSerializer(serializers.ModelSerializer):
    """整改记录序列化器"""
    task_hazard_title = serializers.CharField(source='task.hazard.title', read_only=True)
    result_name = serializers.CharField(source='get_result_display', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = RectifyRecord
        fields = ['id', 'task', 'task_hazard_title', 'photos', 'result', 'result_name', 'remark', 'reviewer', 'reviewer_name', 'reviewed_at', 'created_at']
        read_only_fields = ['id', 'created_at']


class RectifyRecordCreateSerializer(serializers.ModelSerializer):
    """整改记录创建序列化器"""

    class Meta:
        model = RectifyRecord
        fields = ['task', 'photos', 'remark']


class SystemLogSerializer(serializers.ModelSerializer):
    """系统日志序列化器"""
    action_name = serializers.CharField(source='get_action_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SystemLog
        fields = ['id', 'user', 'user_name', 'action', 'action_name', 'model_name', 'object_id', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class HazardAnalyzeSerializer(serializers.Serializer):
    """隐患AI分析请求序列化器"""
    description = serializers.CharField(required=False, allow_blank=True, default='')
    photos = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        max_length=5,
        help_text='照片列表，支持 base64 或 URL'
    )


class DashboardStatsSerializer(serializers.Serializer):
    """仪表盘统计数据"""
    today_inspected = serializers.IntegerField()
    today_uninspected = serializers.IntegerField()
    new_hazards = serializers.IntegerField()
    rectified_hazards = serializers.IntegerField()
    pending_hazards = serializers.IntegerField()
    overdue_hazards = serializers.IntegerField()


class NotificationSerializer(serializers.ModelSerializer):
    """消息通知序列化器"""
    category_name = serializers.CharField(source='get_category_display', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'recipient_name', 'category', 'category_name',
                  'title', 'body', 'source_type', 'source_id',
                  'is_read', 'read_at', 'push_sent', 'created_at']
        read_only_fields = ['id', 'created_at', 'push_sent', 'push_sent_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """通知偏好序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = NotificationPreference
        fields = ['id', 'user', 'username', 'in_app_enabled', 'wechat_enabled',
                  'wechat_openid', 'updated_at']
        read_only_fields = ['id', 'updated_at']