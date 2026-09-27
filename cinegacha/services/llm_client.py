# [AGC:START] tool=Cc author=fangkun
from typing import Optional
import httpx
from cinegacha.services.crypto import CryptoService


class LLMClient:
    """统一 LLM 客户端"""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.Client(timeout=60.0)

    def call_deepseek(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "deepseek-chat"
    ) -> str:
        """调用 DeepSeek API"""
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }

        response = self.client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def extract_characters(self, novel_text: str) -> list[dict]:
        """从小说文本提取角色"""
        system_prompt = "你是一个专业的角色分析专家。请从小说文本中提取所有重要角色。"
        user_message = f"""
请分析以下小说文本，提取所有重要角色：

{novel_text[:2000]}

请以 JSON 格式返回，每个角色包含：
- name: 角色名称
- description: 角色描述（50-100字）
- type: 固定为 "角色"

返回格式示例：
[
  {{"name": "明溪", "description": "12岁女孩，活泼可爱...", "type": "角色"}}
]
"""
        response_text = self.call_deepseek(system_prompt, user_message)
        return self._parse_json_response(response_text)

    def extract_scenes(self, novel_text: str) -> list[dict]:
        """从小说文本提取场景"""
        system_prompt = "你是一个专业的场景分析专家。请从小说文本中提取所有重要场景。"
        user_message = f"""
请分析以下小说文本，提取所有重要场景：

{novel_text[:2000]}

请以 JSON 格式返回，每个场景包含：
- name: 场景名称（如"明家祠堂夜晚"）
- description: 场景描述（30-50字）
- type: 固定为 "场景"

返回格式示例：
[
  {{"name": "明家祠堂夜晚", "description": "古色古香的祠堂，月光透过窗棂...", "type": "场景"}}
]
"""
        response_text = self.call_deepseek(system_prompt, user_message)
        return self._parse_json_response(response_text)

    def extract_props(self, novel_text: str) -> list[dict]:
        """从小说文本提取道具"""
        system_prompt = "你是一个专业的道具分析专家。请从小说文本中提取所有重要道具。"
        user_message = f"""
请分析以下小说文本，提取所有重要道具：

{novel_text[:2000]}

请以 JSON 格式返回，每个道具包含：
- name: 道具名称（如"林依依的项链"）
- description: 道具描述（20-40字）
- type: 固定为 "道具"

返回格式示例：
[
  {{"name": "婚书", "description": "古老的婚书，泛黄的纸张...", "type": "道具"}}
]
"""
        response_text = self.call_deepseek(system_prompt, user_message)
        return self._parse_json_response(response_text)

    def _parse_json_response(self, text: str) -> list[dict]:
        """解析 JSON 响应"""
        import json
        import re

        # 提取 JSON 部分
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                return []
        return []
# [AGC:END]
