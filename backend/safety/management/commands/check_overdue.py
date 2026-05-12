"""
定时检查逾期命令
用法: python manage.py check_overdue
建议通过 Windows 计划任务每小时执行一次
"""
from django.core.management.base import BaseCommand
from safety.notification_service import NotificationService


class Command(BaseCommand):
    help = '检查巡检逾期和整改期限，发送通知'

    def handle(self, *args, **options):
        self.stdout.write('开始检查逾期...')

        self.stdout.write('  [1/2] 检查巡检逾期...')
        inspection_count = NotificationService.check_inspection_overdue()
        self.stdout.write(f'  巡检逾期通知: {inspection_count} 条')

        self.stdout.write('  [2/2] 检查整改期限...')
        rect_count = NotificationService.check_rectify_deadline()
        self.stdout.write(f'  整改期限通知: {rect_count} 条')

        total = inspection_count + rect_count
        self.stdout.write(self.style.SUCCESS(f'检查完成，共发送 {total} 条通知'))
