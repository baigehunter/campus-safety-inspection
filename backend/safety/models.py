from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """用户角色权限表 - 扩展默认用户模型"""
    ROLE_CHOICES = [
        ('admin', '超级管理员'),
        ('safety_manager', '安全管理员'),
        ('inspector', '巡检员'),
        ('rectifier', '整改负责人'),
    ]

    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='inspector')
    phone = models.CharField('手机号', max_length=20, blank=True, null=True)
    avatar = models.ImageField('头像', upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'safety_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class CampusArea(models.Model):
    """校园区域信息表"""
    name = models.CharField('区域名称', max_length=100)
    code = models.CharField('区域编码', max_length=50, unique=True)
    area_type = models.CharField(
        '区域类型',
        max_length=20,
        choices=[
            ('building', '教学楼'),
            ('dormitory', '宿舍楼'),
            ('canteen', '食堂'),
            ('playground', '操场'),
            ('corridor', '楼道'),
            ('fire_exit', '消防通道'),
            ('other', '其他'),
        ]
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级区域'
    )
    description = models.TextField('描述', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'campus_area'
        verbose_name = '校园区域'
        verbose_name_plural = '校园区域'
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.get_area_type_display()})"


class InspectionPoint(models.Model):
    """巡检点位明细表"""
    name = models.CharField('点位名称', max_length=100)
    code = models.CharField('点位编码', max_length=50, unique=True)
    area = models.ForeignKey(
        CampusArea,
        on_delete=models.CASCADE,
        related_name='points',
        verbose_name='所属区域'
    )
    location = models.CharField('具体位置', max_length=200)
    inspection_frequency = models.CharField(
        '巡检频次',
        max_length=20,
        choices=[
            ('daily', '每日'),
            ('weekly', '每周'),
            ('monthly', '每月'),
        ],
        default='daily'
    )
    inspection_content = models.TextField('巡检内容', blank=True)
    responsible_users = models.ManyToManyField(
        User,
        related_name='responsible_points',
        blank=True,
        verbose_name='负责巡检人员'
    )
    is_active = models.BooleanField('是否启用', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'inspection_point'
        verbose_name = '巡检点位'
        verbose_name_plural = '巡检点位'
        ordering = ['sort_order', 'code']

    def __str__(self):
        return f"{self.name} - {self.area.name}"


class InspectionRecord(models.Model):
    """日常巡检记录表"""
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('abnormal', '异常'),
    ]

    point = models.ForeignKey(
        InspectionPoint,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='巡检点位'
    )
    inspector = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inspection_records',
        verbose_name='巡检人'
    )
    status = models.CharField('巡检状态', max_length=20, choices=STATUS_CHOICES)
    inspection_photos = models.JSONField('巡检照片', default=list)
    remark = models.TextField('备注说明', blank=True)
    inspection_time = models.DateTimeField('巡检时间', default=timezone.now)
    # AI 分析字段
    ai_status = models.CharField('AI判断状态', max_length=20, blank=True)
    ai_tags = models.JSONField('AI标签', default=list)
    ai_analysis = models.TextField('AI分析结论', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'inspection_record'
        verbose_name = '巡检记录'
        verbose_name_plural = '巡检记录'
        ordering = ['-inspection_time']

    def __str__(self):
        return f"{self.point.name} - {self.get_status_display()} - {self.inspection_time}"


class HazardReport(models.Model):
    """安全隐患上报表"""
    LEVEL_CHOICES = [
        ('general', '一般隐患'),
        ('serious', '重大安全隐患'),
    ]

    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('assigned', '已派单'),
        ('rectifying', '整改中'),
        ('completed', '已完成'),
        ('rejected', '已驳回'),
    ]

    title = models.CharField('隐患标题', max_length=200)
    description = models.TextField('隐患描述')
    hazard_type = models.CharField(
        '隐患类型',
        max_length=50,
        choices=[
            ('fire', '消防安全'),
            ('electric', '用电安全'),
            ('building', '建筑安全'),
            ('equipment', '设备安全'),
            ('food', '食品安全'),
            ('other', '其他'),
        ]
    )
    level = models.CharField('隐患等级', max_length=20, choices=LEVEL_CHOICES, default='general')
    area = models.ForeignKey(
        CampusArea,
        on_delete=models.SET_NULL,
        null=True,
        related_name='hazards',
        verbose_name='所在区域'
    )
    point = models.ForeignKey(
        InspectionPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hazards',
        verbose_name='关联点位'
    )
    location = models.CharField('具体位置', max_length=200)
    photos = models.JSONField('隐患照片', default=list)
    reporter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_hazards',
        verbose_name='上报人'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateTimeField('整改截止时间', null=True, blank=True)
    # AI 分析字段
    ai_tags = models.JSONField('AI标签', default=list)
    ai_analysis = models.TextField('AI分析结论', blank=True)
    ai_hazard_type = models.CharField('AI判断隐患类型', max_length=50, blank=True)
    ai_level = models.CharField('AI判断隐患等级', max_length=20, blank=True)
    created_at = models.DateTimeField('上报时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'hazard_report'
        verbose_name = '安全隐患'
        verbose_name_plural = '安全隐患'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class RectifyTask(models.Model):
    """整改任务指派表"""
    STATUS_CHOICES = [
        ('pending', '待整改'),
        ('processing', '整改中'),
        ('submitted', '待验收'),
        ('completed', '已完成'),
        ('rejected', '已驳回'),
    ]

    hazard = models.ForeignKey(
        HazardReport,
        on_delete=models.CASCADE,
        related_name='rectify_tasks',
        verbose_name='关联隐患'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='rectify_tasks',
        verbose_name='整改负责人'
    )
    assigner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks',
        verbose_name='派单人'
    )
    description = models.TextField('整改要求', blank=True)
    deadline = models.DateTimeField('整改截止时间')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('派单时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'rectify_task'
        verbose_name = '整改任务'
        verbose_name_plural = '整改任务'
        ordering = ['-created_at']

    def __str__(self):
        return f"整改任务 - {self.hazard.title}"


class RectifyRecord(models.Model):
    """整改复查验收表"""
    RESULT_CHOICES = [
        ('passed', '验收通过'),
        ('rejected', '验收驳回'),
    ]

    task = models.ForeignKey(
        RectifyTask,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='关联整改任务'
    )
    photos = models.JSONField('整改后照片', default=list)
    result = models.CharField('验收结果', max_length=20, choices=RESULT_CHOICES, null=True, blank=True)
    remark = models.TextField('验收备注', blank=True)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='review_records',
        verbose_name='验收人'
    )
    reviewed_at = models.DateTimeField('验收时间', null=True, blank=True)
    created_at = models.DateTimeField('提交时间', auto_now_add=True)

    class Meta:
        db_table = 'rectify_record'
        verbose_name = '整改记录'
        verbose_name_plural = '整改记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"整改记录 - {self.task.hazard.title}"


class SystemLog(models.Model):
    """系统操作日志表"""
    ACTION_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('export', '导出'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='操作人'
    )
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField('操作模型', max_length=50)
    object_id = models.IntegerField('操作对象ID', null=True, blank=True)
    description = models.TextField('操作描述', blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'system_log'
        verbose_name = '系统日志'
        verbose_name_plural = '系统日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} - {self.created_at}"


class Notification(models.Model):
    """消息通知表"""
    CATEGORY_CHOICES = [
        ('hazard_new', '新隐患上报'),
        ('hazard_assigned', '隐患已派单'),
        ('rectify_submitted', '整改已提交'),
        ('rectify_approved', '整改已通过'),
        ('rectify_rejected', '整改已驳回'),
        ('inspection_overdue', '巡检逾期提醒'),
        ('ai_abnormal', 'AI异常检测'),
        ('deadline_approaching', '截止时间临近'),
        ('deadline_overdue', '整改已逾期'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收人'
    )
    category = models.CharField('通知类别', max_length=30, choices=CATEGORY_CHOICES)
    title = models.CharField('通知标题', max_length=200)
    body = models.TextField('通知内容')
    source_type = models.CharField('关联类型', max_length=30, blank=True)
    source_id = models.IntegerField('关联ID', null=True, blank=True)
    is_read = models.BooleanField('已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    push_sent = models.BooleanField('已推送', default=False)
    push_sent_at = models.DateTimeField('推送时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'notification'
        verbose_name = '消息通知'
        verbose_name_plural = '消息通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.get_category_display()} - {self.recipient.username}"


class NotificationPreference(models.Model):
    """通知偏好设置表"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='用户'
    )
    in_app_enabled = models.JSONField('站内通知开关', default=dict)
    wechat_enabled = models.JSONField('微信推送开关', default=dict)
    wechat_openid = models.CharField('微信OpenID', max_length=128, blank=True, default='')
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'notification_preference'
        verbose_name = '通知偏好'
        verbose_name_plural = '通知偏好'

    def __str__(self):
        return f"通知偏好 - {self.user.username}"