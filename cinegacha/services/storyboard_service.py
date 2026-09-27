# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import json
from typing import Optional
from cinegacha import db, Base
from cinegacha.models.script import Script
from cinegacha.models.novel import Novel
from cinegacha.models.project import Project
from cinegacha.services.llm_client import LLMClient


class StoryboardService:
    """分镜拆分服务 - Stage 4"""

    def __init__(self):
        self.chunk_size = 900  # 每块最大字符数
        self.parallel_count = 4  # 并行处理块数

    def split_storyboard(
        self,
        project_id: int,
        api_key: str
    ) -> list[Script]:
        """
        执行分镜拆分

        Args:
            project_id: 项目 ID
            api_key: DeepSeek API key

        Returns:
            list[Script]: 生成的分镜列表
        """
        # 获取项目
        project = db.session.get(Project, project_id)
        if not project:
            raise ValueError(f"项目 {project_id} 不存在")

        # 获取小说
        novel = db.session.get(Novel, project.novel_id)
        if not novel or not novel.content:
            raise ValueError("小说内容为空")

        # 分块
        chunks = self._chunk_text(novel.content, self.chunk_size)

        # 并行处理（简化为串行，实际应使用线程池）
        all_shots = []
        llm_client = LLMClient(api_key=api_key)

        for chunk in chunks:
            shots = self._process_chunk(chunk, llm_client)
            all_shots.extend(shots)

        # 保存到数据库
        scripts = []
        for idx, shot in enumerate(all_shots):
            script = Script(
                project_id=project_id,
                shot_id=idx + 1,
                shot_index=idx + 1,
                content=shot.get("content", ""),
                presets=json.dumps(shot.get("presets", []), ensure_ascii=False)
            )
            db.session.add(script)
            scripts.append(script)

        db.session.commit()
        return scripts

    def _chunk_text(self, text: str, chunk_size: int) -> list[str]:
        """将文本分成多个块"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end
        return chunks

    def _process_chunk(self, chunk: str, llm_client: LLMClient) -> list[dict]:
        """处理单个文本块"""
        system_prompt = "你是一个专业的分镜师。请将文本拆分成适合漫画分镜的镜头。"
        user_message = f"""
请将以下文本拆分成漫画分镜镜头：

{chunk}

请以 JSON 格式返回，每个镜头包含：
- content: 镜头描述文本（100-200字）
- presets: 出场资产列表（角色名、场景名、道具名）

返回格式示例：
[
  {{
    "content": "明溪站在祠堂门口，月光洒在她身上...",
    "presets": ["明溪", "明家祠堂夜晚"]
  }}
]
"""
        response_text = llm_client.call_deepseek(system_prompt, user_message)
        return llm_client._parse_json_response(response_text)

    def get_scripts(self, project_id: int) -> list[Script]:
        """获取项目的所有分镜"""
        return (
            db.session.query(Script)
            .filter(Script.project_id == project_id)
            .order_by(Script.shot_index)
            .all()
        )

    def get_script(self, script_id: int) -> Optional[Script]:
        """获取单个分镜"""
        return db.session.get(Script, script_id)

    def update_script(self, script_id: int, **kwargs) -> Script:
        """更新分镜"""
        script = db.session.get(Script, script_id)
        if not script:
            raise ValueError(f"分镜 {script_id} 不存在")

        for key, value in kwargs.items():
            if hasattr(script, key):
                setattr(script, key, value)

        db.session.commit()
        return script

    def delete_script(self, script_id: int) -> bool:
        """删除分镜"""
        script = db.session.get(Script, script_id)
        if not script:
            return False

        db.session.delete(script)
        db.session.commit()
        return True
