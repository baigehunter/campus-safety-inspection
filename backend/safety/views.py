import logging
from rest_framework import viewsets, status, permissions, throttling

logger = logging.getLogger('safety.api')
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import os
import uuid
from .models import User, CampusArea, InspectionPoint, InspectionRecord, HazardReport, RectifyTask, RectifyRecord, SystemLog, Notification, NotificationPreference
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer,
    CampusAreaSerializer, InspectionPointSerializer,
    InspectionRecordSerializer, InspectionRecordCreateSerializer,
    HazardReportSerializer, HazardReportCreateSerializer,
    HazardAnalyzeSerializer,
    RectifyTaskSerializer, RectifyTaskCreateSerializer,
    RectifyRecordSerializer, RectifyRecordCreateSerializer,
    SystemLogSerializer,
    NotificationSerializer, NotificationPreferenceSerializer
)
from .ai_service import ai_service
from .notification_service import NotificationService
from .permissions import (
    IsAdminUser, IsAdminOrSafetyManager, IsAdminOrSafetyManagerOrReadOnly,
    CanAssignTask, CanReviewTask, CanSubmitRectify, CanResetPassword, CanDeleteUser
)


class LoginRateThrottle(throttling.SimpleRateThrottle):
    """登录限速"""
    rate = '10/minute'
    scope = 'login'

    def get_cache_key(self, request, view):
        # 用 IP 做 key 而不是用户名——防止攻击者用不存在的用户
        # 名反复尝试绕过限速
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request)
        }


class LoginViewSet(viewsets.GenericViewSet):
    """登录视图"""
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_classes = [LoginRateThrottle]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)

        try:
            SystemLog.objects.create(
                user=user,
                action='login',
                model_name='User',
                object_id=user.id,
                description=f'用户 {user.username} 登录系统',
                ip_address=self.get_client_ip(request)
            )
        except Exception:
            pass  # 日志写失败不能阻挡登录，不然用户登不进去

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data
        })

    @staticmethod
    def get_client_ip(request):
        # X-Forwarded-For 可能包含多个 IP（每层代理加一个），
        # 取第一个是原始客户端 IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutViewSet(viewsets.GenericViewSet):
    """登出视图"""
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        try:
            # 将 refresh token 加入黑名单
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            SystemLog.objects.create(
                user=request.user,
                action='logout',
                model_name='User',
                object_id=request.user.id,
                description=f'用户 {request.user.username} 退出系统',
                ip_address=LoginViewSet.get_client_ip(request)
            )
        except Exception:
            pass  # 即使黑名单失败也允许登出

        return Response({'message': '登出成功'})


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSafetyManager]

    def get_permissions(self):
        """根据不同操作设置不同权限"""
        if self.action == 'destroy':
            return [CanDeleteUser()]
        if self.action == 'reset_password':
            return [CanResetPassword()]
        return [IsAdminOrSafetyManager()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset

    def destroy(self, request, *args, **kwargs):
        """禁用用户 - 设置 is_active=False"""
        instance = self.get_object()
        # 禁止禁用自己
        if instance == request.user:
            return Response({'error': '不能禁用自己的账号'}, status=status.HTTP_400_BAD_REQUEST)
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[CanDeleteUser])
    def delete_user(self, request, pk=None):
        """真正删除用户 - 仅超级管理员"""
        instance = self.get_object()
        # 禁止删除自己
        if instance == request.user:
            return Response({'error': '不能删除自己的账号'}, status=status.HTTP_400_BAD_REQUEST)
        # 禁止删除其他超级管理员
        if instance.role == 'admin':
            return Response({'error': '不能删除超级管理员账号'}, status=status.HTTP_400_BAD_REQUEST)
        # 记录日志
        SystemLog.objects.create(
            user=request.user,
            action='delete',
            model_name='User',
            object_id=instance.id,
            description=f'删除用户 {instance.username}',
            ip_address=LoginViewSet.get_client_ip(request)
        )
        # 真正删除用户
        username = instance.username
        instance.delete()
        return Response({'message': f'已删除用户 {username}'})

    @action(detail=False, methods=['post'], permission_classes=[CanResetPassword])
    def reset_password(self, request):
        """重置密码 - 仅管理员"""
        user_id = request.data.get('user_id')
        new_password = request.data.get('new_password')
        if not user_id or not new_password:
            return Response({'error': '参数不完整'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'error': '密码长度至少6位'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            return Response({'message': '密码重置成功'})
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """修改自己的密码"""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response({'error': '参数不完整'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'error': '密码长度至少6位'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.check_password(old_password):
            return Response({'error': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': '密码修改成功'})


class CampusAreaViewSet(viewsets.ModelViewSet):
    """校园区域管理视图"""
    queryset = CampusArea.objects.all()
    serializer_class = CampusAreaSerializer
    permission_classes = [IsAdminOrSafetyManagerOrReadOnly]

    def get_queryset(self):
        queryset = CampusArea.objects.all()
        area_type = self.request.query_params.get('type')
        if area_type:
            queryset = queryset.filter(area_type=area_type)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class InspectionPointViewSet(viewsets.ModelViewSet):
    """巡检点位管理视图"""
    queryset = InspectionPoint.objects.all()
    serializer_class = InspectionPointSerializer
    permission_classes = [IsAdminOrSafetyManagerOrReadOnly]

    def get_queryset(self):
        queryset = InspectionPoint.objects.select_related('area').prefetch_related('responsible_users')
        area_id = self.request.query_params.get('area')
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        frequency = self.request.query_params.get('frequency')
        if frequency:
            queryset = queryset.filter(inspection_frequency=frequency)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active == 'true')
        return queryset


class InspectionRecordViewSet(viewsets.ModelViewSet):
    """巡检记录管理视图"""
    queryset = InspectionRecord.objects.all()
    serializer_class = InspectionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return InspectionRecordCreateSerializer
        return InspectionRecordSerializer

    def get_queryset(self):
        queryset = InspectionRecord.objects.select_related('point', 'inspector')
        # 非管理员只能查看自己的记录
        if self.request.user.role == 'inspector':
            queryset = queryset.filter(inspector=self.request.user)
        point_id = self.request.query_params.get('point')
        if point_id:
            queryset = queryset.filter(point_id=point_id)
        inspector_id = self.request.query_params.get('inspector')
        if inspector_id:
            queryset = queryset.filter(inspector_id=inspector_id)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(inspection_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(inspection_time__lte=end_date)
        return queryset

    def perform_create(self, serializer):
        record = serializer.save(inspector=self.request.user)
        if record.ai_status == 'abnormal':
            try:
                NotificationService.notify_ai_abnormal(record)
            except Exception as e:
                logger.error(f'发送AI异常通知失败: {e}')


class HazardReportViewSet(viewsets.ModelViewSet):
    """安全隐患管理视图"""
    queryset = HazardReport.objects.all()
    serializer_class = HazardReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return HazardReportCreateSerializer
        return HazardReportSerializer

    def get_queryset(self):
        queryset = HazardReport.objects.select_related('area', 'point', 'reporter')
        # 非管理员只能查看自己上报的隐患
        if self.request.user.role == 'inspector':
            queryset = queryset.filter(reporter=self.request.user)
        # 整改负责人只能看到分配给自己的隐患
        if self.request.user.role == 'rectifier':
            queryset = queryset.filter(
                Q(reporter=self.request.user) | Q(tasks__assignee=self.request.user)
            ).distinct()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        hazard_type = self.request.query_params.get('type')
        if hazard_type:
            queryset = queryset.filter(hazard_type=hazard_type)
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        return queryset

    def perform_create(self, serializer):
        hazard = serializer.save(reporter=self.request.user)
        try:
            NotificationService.notify_new_hazard(hazard)
        except Exception as e:
            logger.error(f'发送新隐患通知失败: {e}')

    @action(detail=True, methods=['post'], permission_classes=[CanAssignTask])
    def assign(self, request, pk=None):
        """指派整改任务 - 仅管理员/安全管理员"""
        hazard = self.get_object()

        # 检查隐患状态
        if hazard.status not in ['pending', 'rejected']:
            return Response({'error': '该隐患当前状态不支持派单'}, status=status.HTTP_400_BAD_REQUEST)

        assignee_id = request.data.get('assignee_id')
        description = request.data.get('description', '')
        deadline = request.data.get('deadline')

        if not assignee_id or not deadline:
            return Response({'error': '参数不完整'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignee = User.objects.get(id=assignee_id, role='rectifier')
        except User.DoesNotExist:
            return Response({'error': '整改负责人不存在或角色不正确'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            task = RectifyTask.objects.create(
                hazard=hazard,
                assignee=assignee,
                assigner=request.user,
                description=description,
                deadline=deadline
            )
            hazard.status = 'assigned'
            hazard.save()

        try:
            NotificationService.notify_task_assigned(task)
        except Exception as e:
            logger.error(f'发送任务派单通知失败: {e}')

        return Response(RectifyTaskSerializer(task).data)


class RectifyTaskViewSet(viewsets.ModelViewSet):
    """整改任务管理视图"""
    queryset = RectifyTask.objects.all()
    serializer_class = RectifyTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RectifyTaskCreateSerializer
        return RectifyTaskSerializer

    def get_queryset(self):
        queryset = RectifyTask.objects.select_related('hazard', 'assignee', 'assigner')
        # 整改负责人只能看到自己的任务
        if self.request.user.role == 'rectifier':
            queryset = queryset.filter(assignee=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        assignee_id = self.request.query_params.get('assignee')
        if assignee_id:
            queryset = queryset.filter(assignee_id=assignee_id)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[CanSubmitRectify])
    def submit_rectify(self, request, pk=None):
        """提交整改完成 - 仅整改负责人本人"""
        task = self.get_object()

        # 检查任务状态
        if task.status not in ['pending', 'processing', 'rejected']:
            return Response({'error': '该任务当前状态不支持提交'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否是任务负责人
        if task.assignee != request.user:
            return Response({'error': '只能提交自己负责的任务'}, status=status.HTTP_403_FORBIDDEN)

        photos = request.data.get('photos', [])
        remark = request.data.get('remark', '')

        record = None
        with transaction.atomic():
            record = RectifyRecord.objects.create(
                task=task,
                photos=photos,
                remark=remark
            )
            task.status = 'submitted'
            task.hazard.status = 'rectifying'
            task.save()
            task.hazard.save()

        if record:
            try:
                NotificationService.notify_rectify_submitted(task, record)
            except Exception as e:
                logger.error(f'发送整改提交通知失败: {e}')

        return Response({'message': '整改已提交，等待验收'})

    @action(detail=True, methods=['post'], permission_classes=[CanReviewTask])
    def review(self, request, pk=None):
        """验收整改 - 仅管理员/安全管理员"""
        task = self.get_object()

        # 检查任务状态
        if task.status != 'submitted':
            return Response({'error': '该任务当前状态不支持验收'}, status=status.HTTP_400_BAD_REQUEST)

        result = request.data.get('result')
        remark = request.data.get('remark', '')

        if result not in ['passed', 'rejected']:
            return Response({'error': '验收结果无效'}, status=status.HTTP_400_BAD_REQUEST)

        record = None
        with transaction.atomic():
            record = task.records.last()
            if record:
                record.result = result
                record.remark = remark
                record.reviewer = request.user
                record.reviewed_at = timezone.now()
                record.save()

            if result == 'passed':
                task.status = 'completed'
                task.hazard.status = 'completed'
            else:
                task.status = 'rejected'
                task.hazard.status = 'rectifying'

            task.save()
            task.hazard.save()

        if record:
            try:
                NotificationService.notify_rectify_reviewed(task, record)
            except Exception as e:
                logger.error(f'发送验收结果通知失败: {e}')

        return Response({'message': '验收完成'})


class RectifyRecordViewSet(viewsets.ModelViewSet):
    """整改记录管理视图"""
    queryset = RectifyRecord.objects.all()
    serializer_class = RectifyRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RectifyRecordCreateSerializer
        return RectifyRecordSerializer

    def get_queryset(self):
        queryset = RectifyRecord.objects.select_related('task', 'reviewer')
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset


class DashboardViewSet(viewsets.GenericViewSet):
    """仪表盘统计视图"""
    permission_classes = [IsAdminOrSafetyManager]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取统计数据"""
        today = timezone.now().date()

        # 修复：之前用 records count 当已巡检数，但一个点位被巡多次
        # 算了好几次。改 distinct('point') 去重
        today_records = InspectionRecord.objects.filter(inspection_time__date=today)
        today_inspected = today_records.values('point').distinct().count()

        all_active_points = InspectionPoint.objects.filter(is_active=True).count()
        today_uninspected = max(0, all_active_points - today_inspected)

        new_hazards = HazardReport.objects.filter(created_at__date=today).count()
        rectified_hazards = HazardReport.objects.filter(status='completed').count()
        pending_hazards = HazardReport.objects.exclude(status='completed').count()

        overdue_hazards = HazardReport.objects.filter(
            deadline__lt=timezone.now(),
            status__in=['pending', 'assigned', 'rectifying']
        ).count()

        return Response({
            'today_inspected': today_inspected,
            'today_uninspected': today_uninspected,
            'new_hazards': new_hazards,
            'rectified_hazards': rectified_hazards,
            'pending_hazards': pending_hazards,
            'overdue_hazards': overdue_hazards
        })

    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """获取图表数据"""
        days = []
        for i in range(6, -1, -1):
            date = timezone.now().date() - timedelta(days=i)
            count = InspectionRecord.objects.filter(inspection_time__date=date).count()
            days.append({'date': str(date), 'count': count})

        hazard_types = HazardReport.objects.values('hazard_type').annotate(count=Count('id'))
        type_data = [{'type': item['hazard_type'], 'count': item['count']} for item in hazard_types]

        area_hazards = HazardReport.objects.exclude(area__isnull=True).values('area__name').annotate(count=Count('id'))
        area_data = [{'area': item['area__name'], 'count': item['count']} for item in area_hazards]

        return Response({
            'trend': days,
            'hazard_types': type_data,
            'area_hazards': area_data
        })


class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    """系统日志视图"""
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = SystemLog.objects.select_related('user')
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        # 修复：不要在这里切片，让 DRF 分页处理
        return queryset.order_by('-created_at')


# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class FileUploadView(APIView):
    """文件上传视图"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': '未找到文件'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件类型
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response({
                'error': f'不支持的文件类型，仅支持: {", ".join(ALLOWED_EXTENSIONS)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件大小
        if file_obj.size > MAX_FILE_SIZE:
            return Response({'error': '文件大小不能超过10MB'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}{ext}"

        # 创建保存目录
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        # 返回文件URL
        file_url = f"{settings.MEDIA_URL}uploads/{filename}"
        return Response({'url': file_url, 'filename': filename})


class HazardAnalyzeView(APIView):
    """隐患AI分析视图 - 上传照片+描述，返回AI分析结果"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = HazardAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        description = serializer.validated_data.get('description', '')
        photos = serializer.validated_data.get('photos', [])

        if not description and not photos:
            return Response({'error': '请提供隐患描述或照片'}, status=status.HTTP_400_BAD_REQUEST)

        if not ai_service.is_available():
            return Response({
                'error': 'AI服务未配置，请在 .env 中设置 AI_API_KEY',
                'fallback': {
                    'hazard_type': 'other',
                    'level': 'general',
                    'tags': [],
                    'analysis': ''
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        result = ai_service.analyze_hazard(description, photos)

        if result is None:
            return Response({
                'error': 'AI分析失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result)


class InspectionAnalyzeView(APIView):
    """巡检AI分析视图 - 上传照片+备注，返回AI分析结果"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = HazardAnalyzeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        description = serializer.validated_data.get('description', '')
        photos = serializer.validated_data.get('photos', [])

        if not photos:
            return Response({'error': '请提供巡检照片'}, status=status.HTTP_400_BAD_REQUEST)

        if not ai_service.is_available():
            return Response({
                'error': 'AI服务未配置，请在 .env 中设置 AI_API_KEY'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        result = ai_service.analyze_inspection(description, photos)

        if result is None:
            return Response({
                'error': 'AI分析失败，请稍后重试'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result)


class NotificationViewSet(viewsets.GenericViewSet):
    """消息通知视图"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def list(self, request):
        """获取当前用户的通知列表"""
        queryset = Notification.objects.filter(recipient=request.user)

        is_read = request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read == 'true')

        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        total = queryset.count()
        results = NotificationSerializer(queryset[start:end], many=True).data

        return Response({'count': total, 'results': results})

    @action(detail=False, methods=['post'])
    def read_all(self, request):
        """全部标记为已读"""
        now = timezone.now()
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_at=now
        )
        return Response({'message': '已全部标记为已读'})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记单条为已读"""
        try:
            notification = Notification.objects.get(id=pk, recipient=request.user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return Response({'message': '已标记为已读'})
        except Notification.DoesNotExist:
            return Response({'error': '通知不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读数量"""
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'total_unread': count})


class NotificationPreferenceViewSet(viewsets.GenericViewSet):
    """通知偏好视图"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer

    def retrieve(self, request):
        """获取当前用户的偏好"""
        from .models import Notification
        pref, _ = NotificationPreference.objects.get_or_create(
            user=request.user,
            defaults={
                'in_app_enabled': {cat: True for cat in dict(Notification.CATEGORY_CHOICES)},
                'wechat_enabled': {cat: True for cat in dict(Notification.CATEGORY_CHOICES)},
            }
        )
        return Response(NotificationPreferenceSerializer(pref).data)

    def update(self, request):
        """更新偏好"""
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(pref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class WeChatViewSet(viewsets.GenericViewSet):
    """微信小程序接口"""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def get_openid(self, request):
        """用 wx.login() 返回的 code 换取 openid"""
        code = request.data.get('code')
        if not code:
            return Response({'error': '缺少 code 参数'}, status=status.HTTP_400_BAD_REQUEST)

        appid = getattr(settings, 'WX_APPID', '')
        secret = getattr(settings, 'WX_SECRET', '')
        if not appid or not secret:
            return Response({'error': '微信未配置'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            import requests as http_requests
            resp = http_requests.get(
                'https://api.weixin.qq.com/sns/jscode2session',
                params={
                    'appid': appid,
                    'secret': secret,
                    'js_code': code,
                    'grant_type': 'authorization_code'
                },
                timeout=5
            )
            data = resp.json()
        except Exception as e:
            logger.error(f'换取 openid 失败: {e}')
            return Response({'error': '微信服务请求失败'}, status=status.HTTP_502_BAD_GATEWAY)

        openid = data.get('openid')
        if not openid:
            errmsg = data.get('errmsg', '未知错误')
            logger.error(f'code2Session 失败: {data}')
            return Response({'error': f'获取 openid 失败: {errmsg}'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存 openid
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
        pref.wechat_openid = openid
        pref.save()
        return Response({'openid': openid})

    @action(detail=False, methods=['get'])
    def templates(self, request):
        """返回配置的微信订阅消息模板 ID 列表"""
        template_ids = getattr(settings, 'WX_TEMPLATE_IDS', {})
        # 只返回已配置的模板
        return Response({k: v for k, v in template_ids.items() if v})

    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """更新用户订阅的模板列表"""
        templates = request.data.get('templates', [])
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)

        # templates 是用户同意订阅的模板列表（内部 category 名称）
        # 更新 wechat_enabled：只有用户明确订阅的才设为 True
        from .models import Notification
        all_categories = dict(Notification.CATEGORY_CHOICES)
        for cat in all_categories:
            pref.wechat_enabled[cat] = cat in templates

        pref.save()
        return Response(NotificationPreferenceSerializer(pref).data)
