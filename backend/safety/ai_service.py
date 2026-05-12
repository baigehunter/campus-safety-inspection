"""
校园安全 AI 分析服务
支持豆包（火山方舟）等兼容 OpenAI 接口的大模型
"""
import os
import json
import logging
from typing import Optional

logger = logging.getLogger('safety.ai')
OpenAI = None


class AIService:
    """AI 分析服务 - 隐患智能识别"""

    def __init__(self):
        self.client = None
        self.model = os.environ.get('AI_MODEL', 'doubao-seed-2-0-lite-260428')
        self.max_tokens = int(os.environ.get('AI_MAX_TOKENS', '500'))
        self.temperature = float(os.environ.get('AI_TEMPERATURE', '0.3'))
        api_key = os.environ.get('AI_API_KEY', '')
        api_base = os.environ.get('AI_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3')

        if not api_key:
            logger.warning('AI_API_KEY not configured, AI service disabled')
            return

        global OpenAI
        if OpenAI is None:
            try:
                from openai import OpenAI as _OpenAI
                OpenAI = _OpenAI
            except ImportError:
                logger.warning('openai package not installed, AI service disabled')
                return

        self.client = OpenAI(api_key=api_key, base_url=api_base)

    def is_available(self) -> bool:
        return self.client is not None

    def analyze_hazard(self, description: str, photos: list[str]) -> Optional[dict]:
        """分析隐患照片，返回隐患类型、等级、标签、分析结论"""
        if not self.is_available():
            return None

        # 构建完整的提示词（包含系统指令）
        full_prompt = (
            "你是一个校园安全巡检专家。请分析以下隐患描述"
            + ("和照片" if photos else "")
            + "，判断是否存在安全隐患。\n"
            "严格按照JSON格式返回，不要输出其他内容。\n"
            "如果无明显安全隐患，hazard_type 返回 'other'，level 返回 'general'。\n\n"
            f"隐患描述：{description}\n\n"
            "请分析并返回JSON：\n"
            "{\n"
            '  "hazard_type": "fire|electric|building|equipment|food|other",\n'
            '  "level": "general|serious",\n'
            '  "tags": ["标签1", "标签2"],\n'
            '  "analysis": "详细分析结论（50-200字）"\n'
            "}\n\n"
            "隐患类型说明：\n"
            "- fire: 消防安全（灭火器、消防栓、疏散通道等）\n"
            "- electric: 用电安全（电线、配电箱、插座等）\n"
            "- building: 建筑安全（墙体、地面、门窗、护栏等）\n"
            "- equipment: 设备安全（监控、报警器、空调等）\n"
            "- food: 食品安全（食材、厨房卫生等）\n"
            "- other: 其他/无明显隐患\n\n"
            "隐患等级说明：\n"
            "- general: 一般隐患（可限期整改）\n"
            "- serious: 重大安全隐患（需立即处理）"
        )

        try:
            # 构建用户消息内容（豆包 Responses API 格式）
            content = [{"type": "input_text", "text": full_prompt}]

            for photo in photos:
                if photo.startswith('data:'):
                    image_url = photo
                elif photo.startswith('http'):
                    image_url = photo
                else:
                    # 纯 base64，添加前缀
                    image_url = f"data:image/jpeg;base64,{photo}"

                content.append({
                    "type": "input_image",
                    "image_url": image_url
                })

            # Responses API 格式（根据火山方舟文档）
            input_data = [
                {
                    "role": "user",
                    "content": content
                }
            ]

            response = self.client.responses.create(
                model=self.model,
                input=input_data,
            )

            # 提取返回文本
            content_text = response.output_text

            # 清理可能的 markdown 代码块标记
            if content_text.startswith("```"):
                lines = content_text.split("\n")
                content_text = "\n".join(lines[1:]) if len(lines) > 1 else content_text
            if content_text.endswith("```"):
                content_text = content_text[:-3].strip()

            result = json.loads(content_text)
            logger.info(f"AI analysis result: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {content_text}, error: {e}")
            return None
        except Exception as e:
            # 图片请求失败，降级为纯文字分析
            if photos:
                logger.warning(f"Vision request failed, falling back to text-only: {e}")
                return self._analyze_text_only(full_prompt)
            logger.error(f"AI analysis failed: {e}")
            return None

    def _analyze_text_only(self, prompt: str) -> Optional[dict]:
        """纯文字分析降级方案"""
        try:
            input_data = [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}]
                }
            ]

            response = self.client.responses.create(
                model=self.model,
                input=input_data,
            )

            content_text = response.output_text

            if content_text.startswith("```"):
                lines = content_text.split("\n")
                content_text = "\n".join(lines[1:]) if len(lines) > 1 else content_text
            if content_text.endswith("```"):
                content_text = content_text[:-3].strip()

            result = json.loads(content_text)
            logger.info(f"AI text-only result: {result}")
            return result

        except Exception as e:
            logger.error(f"Text-only analysis also failed: {e}")
            return None

    def analyze_inspection(self, remark: str, photos: list[str]) -> Optional[dict]:
        """分析巡检照片，返回巡检状态判断、标签、分析结论"""
        if not self.is_available():
            return None

        full_prompt = (
            "你是一个校园安全巡检专家。请分析以下巡检照片"
            + ("和备注" if remark else "")
            + "，判断巡检点位的安全状况。\n"
            "严格按照JSON格式返回，不要输出其他内容。\n"
            "如果照片显示一切正常，status 返回 'normal'。\n\n"
            + (f"巡检备注：{remark}\n\n" if remark else "")
            + "请分析并返回JSON：\n"
            "{\n"
            '  "status": "normal|abnormal",\n'
            '  "tags": ["标签1", "标签2"],\n'
            '  "analysis": "详细分析结论（50-200字）"\n'
            "}\n\n"
            "status 判断标准：\n"
            "- normal: 设备/设施完好，无安全隐患，环境整洁\n"
            "- abnormal: 存在破损、缺失、异常状况或安全风险\n"
        )

        try:
            content = [{"type": "input_text", "text": full_prompt}]

            for photo in photos:
                if photo.startswith('data:'):
                    image_url = photo
                elif photo.startswith('http'):
                    image_url = photo
                else:
                    image_url = f"data:image/jpeg;base64,{photo}"

                content.append({
                    "type": "input_image",
                    "image_url": image_url
                })

            input_data = [{"role": "user", "content": content}]

            response = self.client.responses.create(
                model=self.model,
                input=input_data,
            )

            content_text = response.output_text

            if content_text.startswith("```"):
                lines = content_text.split("\n")
                content_text = "\n".join(lines[1:]) if len(lines) > 1 else content_text
            if content_text.endswith("```"):
                content_text = content_text[:-3].strip()

            result = json.loads(content_text)
            logger.info(f"AI inspection result: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI inspection response: {content_text}, error: {e}")
            return None
        except Exception as e:
            if photos:
                logger.warning(f"Vision inspection request failed, falling back to text-only: {e}")
                return self._analyze_inspection_text_only(full_prompt)
            logger.error(f"AI inspection analysis failed: {e}")
            return None

    def _analyze_inspection_text_only(self, prompt: str) -> Optional[dict]:
        """纯文字分析降级方案（巡检）"""
        try:
            input_data = [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}]
                }
            ]

            response = self.client.responses.create(
                model=self.model,
                input=input_data,
            )

            content_text = response.output_text

            if content_text.startswith("```"):
                lines = content_text.split("\n")
                content_text = "\n".join(lines[1:]) if len(lines) > 1 else content_text
            if content_text.endswith("```"):
                content_text = content_text[:-3].strip()

            result = json.loads(content_text)
            logger.info(f"AI inspection text-only result: {result}")
            return result

        except Exception as e:
            logger.error(f"Text-only inspection analysis also failed: {e}")
            return None


# 全局单例
ai_service = AIService()
