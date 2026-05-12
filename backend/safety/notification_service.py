"""
消息通知服务 - 在业务事件触发点调用，创建通知记录并推送微信订阅消息
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('safety.notification')


class NotificationService:
    """通知服务 - 所有方法均为静态方法，在视图中直接调用"""

    # ── 模板ID 映射 ──────────────────────────────────────
    TEMPLATE_MAP = {
        'hazard_new': 'hazard_new',
        'hazard_assigned': 'hazard_assigned',
        'rectify_submitted': 'rectify_result',
        'rectify_approved': 'rectify_result',
        'rectify_rejected': 'rectify_result',
        'inspection_overdue': 'inspection_overdue',
        'ai_abnormal': 'ai_abnormal',
        'deadline_approaching': 'hazard_assigned',
        'deadline_overdue': 'hazard_assigned',
    }

    # ── 推送入口 ────────────────────────────────────────

    @staticmethod
    def _try_push(notification):
        """尝试推送微信订阅消息（best-effort，失败不抛异常）"""
        try:
            template_names = getattr(settings, 'WX_TEMPLATE_IDS', {})
            template_key = NotificationService.TEMPLATE_MAP.get(notification.category)
            template_id = template_names.get(template_key, '') if template_key else ''
            if not template_id:
                return

            from .models import NotificationPreference
            try:
                pref = NotificationPreference.objects.get(user=notification.recipient)
            except NotificationPreference.DoesNotExist:
                return

            openid = pref.wechat_openid
            if not openid:
                return

            if not pref.wechat_enabled.get(notification.category, False):
                return

            from .wechat_push import WeChatPushService
            wx_data = NotificationService._build_wx_data(notification)
            result = WeChatPushService.send(openid, template_id, wx_data)

            if result and result.get('errcode') == 0:
                notification.push_sent = True
                notification.push_sent_at = timezone.now()
                notification.save()
            else:
                logger.warning(
                    f'微信推送失败: user={notification.recipient.username} '
                    f'category={notification.category} result={result}'
                )
        except Exception as e:
            logger.error(f'推送微信消息异常: {e}')

    @staticmethod
    def _build_wx_data(notification):
        """根据通知类别构造微信订阅消息 data 结构"""
        # 微信模板关键词限制：thing 最多20字符，phrase 最多5字符
        from .models import Notification
        cat = notification.category
        title = notification.title[:20]
        body = notification.body[:20]

        if cat == 'hazard_new':
            return {
                'thing1': {'value': title},
                'thing2': {'value': body},
                'time3': {'value': notification.created_at.strftime('%Y-%m-%d %H:%M')},
            }
        elif cat == 'hazard_assigned':
            return {
                'thing1': {'value': title},
                'thing2': {'value': body},
                'time3': {'value': notification.created_at.strftime('%Y-%m-%d %H:%M')},
            }
        elif cat in ('rectify_submitted', 'rectify_approved', 'rectify_rejected'):
            return {
                'thing1': {'value': title},
                'phrase2': {'value': '通过' if cat == 'rectify_approved' else ('驳回' if cat == 'rectify_rejected' else '提交')},
                'time3': {'value': notification.created_at.strftime('%Y-%m-%d %H:%M')},
            }
        elif cat == 'inspection_overdue':
            return {
                'thing1': {'value': title},
                'thing2': {'value': body},
                'time3': {'value': notification.created_at.strftime('%Y-%m-%d %H:%M')},
            }
        elif cat == 'ai_abnormal':
            return {
                'thing1': {'value': title},
                'thing2': {'value': body},
                'time3': {'value': notification.created_at.strftime('%Y-%m-%d %H:%M')},
            }
        elif cat in ('deadline_approaching', 'deadline_overdue'):
            return {
                'thing1': {'value': title},
                'thing2': {'value': body},
                'time3': {'value': notification.created_at.strftime('%Y-%m-%d %H:%M')},
            }
        # default fallback
        return {
            'thing1': {'value': title},
            'thing2': {'value': body},
        }

    # ── 业务通知方法 ────────────────────────────────────

    @staticmethod
    def notify_new_hazard(hazard):
        """新隐患上报 → 通知所有管理员和安全管理员"""
        from .models import User, Notification
        recipients = User.objects.filter(
            role__in=['admin', 'safety_manager'],
            is_active=True
        )
        for user in recipients:
            n = Notification.objects.create(
                recipient=user,
                category='hazard_new',
                title=f'新隐患上报：{hazard.title}',
                body=f'隐患类型：{hazard.get_hazard_type_display()} | 等级：{hazard.get_level_display()} | 位置：{hazard.location}',
                source_type='hazard',
                source_id=hazard.id
            )
            NotificationService._try_push(n)
        logger.info(f'新隐患通知已发送给 {recipients.count()} 位管理员')

    @staticmethod
    def notify_task_assigned(task):
        """任务派单 → 通知整改负责人"""
        from .models import Notification
        if task.assignee:
            n = Notification.objects.create(
                recipient=task.assignee,
                category='hazard_assigned',
                title=f'您有新的整改任务：{task.hazard.title}',
                body=f'整改要求：{task.description or "请尽快完成整改"} | 截止时间：{task.deadline.strftime("%m月%d日 %H:%M")}',
                source_type='task',
                source_id=task.id
            )
            NotificationService._try_push(n)

    @staticmethod
    def notify_rectify_submitted(task, record):
        """整改已提交 → 通知管理员和安全管理员"""
        from .models import User, Notification
        recipients = User.objects.filter(
            role__in=['admin', 'safety_manager'],
            is_active=True
        )
        for user in recipients:
            n = Notification.objects.create(
                recipient=user,
                category='rectify_submitted',
                title=f'整改已提交验收：{task.hazard.title}',
                body=f'整改人：{task.assignee.username if task.assignee else "-"} | 提交备注：{record.remark or "无"}',
                source_type='task',
                source_id=task.id
            )
            NotificationService._try_push(n)

    @staticmethod
    def notify_rectify_reviewed(task, record):
        """整改验收完成 → 通知整改负责人 和 隐患上报人"""
        from .models import Notification
        result_text = '通过' if record.result == 'passed' else '驳回'
        category = f'rectify_{record.result}' if record.result in ['passed', 'rejected'] else 'rectify_approved'
        title = f'整改验收{result_text}：{task.hazard.title}'
        body = f'验收结果：{record.get_result_display()} | 验收备注：{record.remark or "无"}'

        # 通知整改负责人
        if task.assignee:
            n = Notification.objects.create(
                recipient=task.assignee,
                category=category,
                title=title,
                body=body,
                source_type='task',
                source_id=task.id
            )
            NotificationService._try_push(n)

        # 通知隐患上报人
        if task.hazard.reporter and task.hazard.reporter != task.assignee:
            n = Notification.objects.create(
                recipient=task.hazard.reporter,
                category=category,
                title=title,
                body=body,
                source_type='task',
                source_id=task.id
            )
            NotificationService._try_push(n)

    @staticmethod
    def notify_ai_abnormal(record):
        """AI检测异常 → 通知管理员"""
        from .models import User, Notification
        recipients = User.objects.filter(
            role__in=['admin', 'safety_manager'],
            is_active=True
        )
        for user in recipients:
            n = Notification.objects.create(
                recipient=user,
                category='ai_abnormal',
                title=f'AI检测异常：{record.point.name}',
                body=f'巡检点位：{record.point.name} | AI分析：{record.ai_analysis or "检测到异常状况"} | 巡检人：{record.inspector.username if record.inspector else "-"}',
                source_type='record',
                source_id=record.id
            )
            NotificationService._try_push(n)

    @staticmethod
    def check_inspection_overdue():
        """检查巡检逾期（由定时任务调用）"""
        from .models import InspectionPoint, InspectionRecord, Notification
        now = timezone.now()
        today = now.date()

        points = InspectionPoint.objects.filter(is_active=True).prefetch_related('responsible_users')
        created_count = 0

        for point in points:
            last_record = InspectionRecord.objects.filter(point=point).order_by('-inspection_time').first()

            if point.inspection_frequency == 'daily':
                deadline = now - timedelta(days=1)
                if last_record and last_record.inspection_time > deadline:
                    continue
            elif point.inspection_frequency == 'weekly':
                deadline = now - timedelta(days=7)
                if last_record and last_record.inspection_time > deadline:
                    continue
            elif point.inspection_frequency == 'monthly':
                deadline = now - timedelta(days=30)
                if last_record and last_record.inspection_time > deadline:
                    continue
            else:
                continue

            # 检查是否今天已发过通知（避免重复）
            already_notified = Notification.objects.filter(
                source_type='point',
                source_id=point.id,
                category='inspection_overdue',
                created_at__date=today
            ).exists()
            if already_notified:
                continue

            last_time = last_record.inspection_time.strftime('%m月%d日 %H:%M') if last_record else '从未巡检'
            for user in point.responsible_users.all():
                n = Notification.objects.create(
                    recipient=user,
                    category='inspection_overdue',
                    title=f'巡检逾期提醒：{point.name}',
                    body=f'点位：{point.name}（{point.area.name}）| 频次：{point.get_inspection_frequency_display()} | 上次巡检：{last_time}',
                    source_type='point',
                    source_id=point.id
                )
                NotificationService._try_push(n)
                created_count += 1

        logger.info(f'巡检逾期检查完成，发送了 {created_count} 条通知')
        return created_count

    @staticmethod
    def check_rectify_deadline():
        """检查整改截止时间（由定时任务调用）"""
        from .models import RectifyTask, Notification
        now = timezone.now()
        today = now.date()

        tasks = RectifyTask.objects.filter(
            status__in=['pending', 'processing']
        ).select_related('assignee', 'hazard')

        approaching_count = 0
        overdue_count = 0

        for task in tasks:
            if not task.deadline:
                continue

            # 逾期
            if task.deadline < now:
                already_notified = Notification.objects.filter(
                    source_type='task',
                    source_id=task.id,
                    category='deadline_overdue',
                    created_at__date=today
                ).exists()
                if not already_notified and task.assignee:
                    n = Notification.objects.create(
                        recipient=task.assignee,
                        category='deadline_overdue',
                        title=f'整改已逾期：{task.hazard.title}',
                        body=f'截止时间：{task.deadline.strftime("%m月%d日 %H:%M")} | 已超出期限，请尽快完成整改',
                        source_type='task',
                        source_id=task.id
                    )
                    NotificationService._try_push(n)
                    overdue_count += 1

            # 24小时内到期
            elif task.deadline < now + timedelta(hours=24):
                already_notified = Notification.objects.filter(
                    source_type='task',
                    source_id=task.id,
                    category='deadline_approaching',
                    created_at__date=today
                ).exists()
                if not already_notified and task.assignee:
                    n = Notification.objects.create(
                        recipient=task.assignee,
                        category='deadline_approaching',
                        title=f'整改即将到期：{task.hazard.title}',
                        body=f'截止时间：{task.deadline.strftime("%m月%d日 %H:%M")} | 请在24小时内完成整改',
                        source_type='task',
                        source_id=task.id
                    )
                    NotificationService._try_push(n)
                    approaching_count += 1

        logger.info(f'限期检查完成：{approaching_count} 条临近提醒, {overdue_count} 条逾期提醒')
        return approaching_count + overdue_count


def get_default_preferences():
    """获取默认通知偏好设置"""
    categories = [
        'hazard_new', 'hazard_assigned', 'rectify_submitted',
        'rectify_approved', 'rectify_rejected', 'inspection_overdue',
        'ai_abnormal', 'deadline_approaching', 'deadline_overdue'
    ]
    return {
        cat: True for cat in categories
    }
