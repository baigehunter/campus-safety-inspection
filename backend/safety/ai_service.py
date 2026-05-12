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
            "你是一名校园安全巡检专家，具备建筑安全、消防安全、电气安全等领域的专业知识。\n\n"
            "## 任务\n"
            "根据巡检员提供的隐患描述"
            + ("和现场照片" if photos else "")
            + "，判断是否存在安全隐患，进行分类、定级和分析。\n\n"
            "## 分析步骤\n"
            "1. 仔细观察照片中的所有细节：设备外观是否完好、有无破损/锈蚀/变形/过热痕迹、环境是否整洁、通道是否畅通、标识是否清晰等\n"
            "2. 结合隐患描述，判断是否存在安全风险\n"
            "3. 对照以下分类标准，确定隐患类型和等级\n"
            "4. 给出具体、可操作的结论\n\n"
            "## 隐患类型判定标准\n"
            "- fire（消防安全）：灭火器缺失/过期/压力不足、消防栓损坏/被遮挡/无水、疏散通道堵塞/上锁、应急灯故障、疏散指示缺失、烟感/温感异常、防火门损坏\n"
            "- electric（用电安全）：电线老化/破损/裸露、配电箱异常（过热/积尘/积水/未上锁/无警示标识）、私拉乱接电线、插座烧焦/过载、漏电保护失效、接地不良\n"
            "- building（建筑安全）：墙体裂缝/渗水/倾斜、护栏松动/缺失/高度不足、地面塌陷/积水/油污、门窗破损/无法正常启闭、天花板/吊顶脱落风险、楼梯扶手损坏\n"
            "- equipment（设备安全）：监控摄像头故障/视角偏移、报警器失效/误报、空调外机支架松动、电梯/升降设备异常、锅炉/压力容器超期未检、通风排烟设备故障\n"
            "- food（食品安全）：食材过期/变质、厨房卫生不达标、餐具消毒不到位、食品留样不规范、从业人员健康证过期、三防设施（防蝇/防鼠/防尘）缺失\n"
            "- other：不属于以上类别，或照片中无明显安全隐患\n\n"
            "## 隐患等级判定标准\n"
            "- serious（重大隐患）：可能立即造成人员伤亡或重大财产损失，需24小时内紧急处理。例如：结构性裂缝、裸露带电体、消防通道完全堵塞且堆满易燃物、燃气泄漏\n"
            "- general（一般隐患）：存在安全风险但不会立即造成严重后果，可限期（3-7天）整改。例如：灭火器临近过期、疏散指示牌不亮、物品堆放不规范、标识模糊不清\n\n"
            "## 输出要求\n"
            "- 只返回一个合法的 JSON 对象，不要包含 markdown 代码块标记（```），不要输出任何解释或补充文字\n"
            "- tags 应包含 2-4 个简短中文短语，精准描述问题特征，例如：\"灭火器过期\"、\"电线裸露\"、\"通道堵塞\"、\"护栏松动\"\n"
            "- analysis 应在 80-200 字之间，结构为：①观察到的具体问题 → ②潜在风险 → ③建议处理措施\n"
            "- 如果照片模糊、光线不足、角度不佳导致无法准确判断，请在 analysis 中明确说明\"因照片质量原因，以下分析仅供参考\"，并将 level 设为 general\n"
            "- 如果确实是同一位置同时存在多种类型隐患，以最严重的那一类作为 hazard_type，其他类型在 tags 和 analysis 中补充说明\n\n"
            f"隐患描述：{description}\n\n"
            "请分析并返回JSON：\n"
            "{\n"
            '  "hazard_type": "此处填类型",\n'
            '  "level": "此处填等级",\n'
            '  "tags": ["标签1", "标签2"],\n'
            '  "analysis": "此处填分析结论"\n'
            "}"
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
            "你是一名校园安全巡检专家。\n\n"
            "## 任务\n"
            "根据巡检员拍摄的点位照片"
            + ("和备注信息" if remark else "")
            + "，判断该巡检点位的安全状况是否正常。\n\n"
            "## 检查要点\n"
            "请从以下维度逐一检查照片中的细节：\n"
            "1. **设备/设施本体**：外观是否完好，有无明显损坏、缺失、锈蚀、变形、松动、老化\n"
            "2. **标识与状态指示**：安全标识、铭牌、压力表、指示灯是否正常、清晰可见\n"
            "3. **周围环境**：是否整洁有序，有无杂物堆积、积水、油污，通道是否畅通\n"
            "4. **潜在风险信号**：是否有烟熏痕迹、异常发热痕迹、异味（需从描述判断）、异常声响（需从描述判断）\n"
            "5. 如有巡检备注，请结合备注内容综合判断\n\n"
            "## 判定标准\n"
            "- normal（正常）：以上检查项均无异常，设备/设施完好可用，环境整洁，符合安全管理要求\n"
            "- abnormal（异常）：任一项存在破损、缺失、锈蚀、老化、松动、遮挡、不洁、标识不清等情况，或存在任何安全风险\n\n"
            "## 输出要求\n"
            "- 只返回一个合法的 JSON 对象，不要包含 markdown 代码块标记（```），不要输出任何解释或补充文字\n"
            "- tags 应包含 2-3 个简短中文短语，精准描述当前状态。normal 时可用 \"设备完好\"、\"环境整洁\" 等；abnormal 时描述具体问题\n"
            "- analysis 应在 50-150 字之间：normal 时简洁说明设备状态良好、在正常使用范围内；abnormal 时具体说明观察到的问题以及是否建议转为隐患上报\n"
            "- 如果照片模糊、光线不足或角度不佳导致无法准确判断，请在 analysis 中说明情况并注明\"仅供参考\"\n"
            + (f"\n巡检备注：{remark}\n" if remark else "\n")
            + "\n请分析并返回JSON：\n"
            "{\n"
            '  "status": "normal 或 abnormal",\n'
            '  "tags": ["标签1", "标签2"],\n'
            '  "analysis": "此处填分析结论"\n'
            "}"
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
