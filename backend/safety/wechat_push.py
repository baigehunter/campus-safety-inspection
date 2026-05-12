"""
微信订阅消息推送服务
"""
import requests
import logging
import time
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('safety.wechat')

WX_ACCESS_TOKEN_KEY = 'wechat_access_token'
WX_TOKEN_EXPIRE_BUFFER = 300  # 提前5分钟刷新


class WeChatPushService:
    """微信订阅消息推送"""

    @classmethod
    def send(cls, openid, template_id, data, page=None):
        """发送订阅消息"""
        if not openid or not template_id:
            logger.warning('缺少 openid 或 template_id，跳过推送')
            return None

        access_token = cls._get_access_token()
        if not access_token:
            logger.error('无法获取微信 access_token')
            return None

        payload = {
            'touser': openid,
            'template_id': template_id,
            'page': page or 'pages/index/index',
            'data': data,
        }

        try:
            resp = requests.post(
                f'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}',
                json=payload,
                timeout=5
            )
            result = resp.json()
            if result.get('errcode') != 0:
                logger.error(f'微信推送失败: {result}')
            return result
        except Exception as e:
            logger.error(f'微信推送异常: {e}')
            return None

    @classmethod
    def _get_access_token(cls):
        """获取并缓存 access_token"""
        token = cache.get(WX_ACCESS_TOKEN_KEY)
        if token:
            return token

        appid = getattr(settings, 'WX_APPID', '')
        secret = getattr(settings, 'WX_SECRET', '')

        if not appid or not secret:
            logger.warning('未配置 WX_APPID / WX_SECRET')
            return None

        try:
            resp = requests.get(
                'https://api.weixin.qq.com/cgi-bin/token',
                params={
                    'grant_type': 'client_credential',
                    'appid': appid,
                    'secret': secret
                },
                timeout=5
            )
            data = resp.json()
            access_token = data.get('access_token')
            if access_token:
                expires_in = data.get('expires_in', 7200)
                cache.set(WX_ACCESS_TOKEN_KEY, access_token, max(expires_in - WX_TOKEN_EXPIRE_BUFFER, 60))
                return access_token
            else:
                logger.error(f'获取 access_token 失败: {data}')
                return None
        except Exception as e:
            logger.error(f'获取 access_token 异常: {e}')
            return None
