# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import json
from typing import Optional
from cinegacha import db
from cinegacha.models.script import Script
from cinegacha.models.role import Role, RoleTag
from cinegacha.models.project import Project
from cinegacha.services.llm_client import LLMClient


class DerivationService:
    """图像推导服务 - Stage 5"""

    def __init__(self):
        self.llm_client = None

    def derive_image_prompt(
        self,
        script_id: int,
        api_key: str
    ) -> Script:
        """
        为单个分镜生成图像提示词

        Args:
            script_id: 分镜 ID
            api_key: DeepSeek API key

        Returns:
            Script: 更新后的分镜对象
        """
        script = db.session.get(Script, script_id)
        if not script:
            raise ValueError(f"分镜 {script_id} 不存在")

        if not script.content:
            raise ValueError("分镜内容为空")

        # 初始化 LLM 客户端
        self.llm_client = LLMClient(api_key=api_key)

        # 获取项目信息
        project = db.session.get(Project, script.project_id)
        if not project:
            raise ValueError("项目不存在")

        # 解析出场资产
        presets = json.loads(script.presets) if script.presets else []

        # 匹配资产描述
        asset_context = self._match_assets(presets, script.project_id)

        # 组装提示词
        system_prompt = "你是一个专业的漫画分镜提示词生成器。请根据场景描述生成详细的图像提示词。"
        user_message = self._assemble_prompt(
            story_content=script.content,
            asset_context=asset_context,
            img_prompt_prefix=project.img_prompt_prefix or "",
            img_prompt_suffix=project.img_prompt_suffix or ""
        )

        # 调用 LLM
        image_prompt = self.llm_client.call_deepseek(system_prompt, user_message)

        # 更新分镜
        script.image_prompt = image_prompt
        db.session.commit()

        return script

    def _match_assets(self, presets: list[str], project_id: int) -> dict:
        """匹配资产描述"""
        characters = []
        scenes = []
        props = []

        for preset_name in presets:
            # 查找匹配的资产
            role = (
                db.session.query(Role)
                .filter(Role.project_id == project_id, Role.name == preset_name)
                .first()
            )

            if role:
                # 获取资产类型
                role_type = None
                for tag in role.tags:
                    if tag.tag_category == "类型":
                        role_type = tag.tag_value
                        break

                # 优先使用英文增强描述
                description = role.content_word2 or role.content or ""

                if role_type == "角色":
                    characters.append({"name": role.name, "description": description})
                elif role_type == "场景":
                    scenes.append({"name": role.name, "description": description})
                elif role_type == "道具":
                    props.append({"name": role.name, "description": description})

        return {
            "characters": characters,
            "scenes": scenes,
            "props": props
        }

    def _assemble_prompt(
        self,
        story_content: str,
        asset_context: dict,
        img_prompt_prefix: str,
        img_prompt_suffix: str
    ) -> str:
        """组装完整提示词"""
        # 构建角色列表
        character_list = ", ".join([c["name"] for c in asset_context["characters"]])

        # 构建角色描述
        character_descriptions = "\n".join([
            f"- {c['name']}: {c['description']}"
            for c in asset_context["characters"]
        ])

        # 构建场景描述
        scene_description = "\n".join([
            f"- {s['name']}: {s['description']}"
            for s in asset_context["scenes"]
        ])

        # 构建道具描述
        prop_descriptions = "\n".join([
            f"- {p['name']}: {p['description']}"
            for p in asset_context["props"]
        ])

        user_message = f"""{img_prompt_prefix}

【故事内容】
{story_content}

【出场角色】
{character_list if character_list else "无"}

【角色描述】
{character_descriptions if character_descriptions else "无"}

【场景描述】
{scene_description if scene_description else "无"}

【道具描述】
{prop_descriptions if prop_descriptions else "无"}

{img_prompt_suffix}

请生成 455-1270 字的图像提示词，包含以下结构：
1. 画面描述（40%）：视觉内容、人物、姿势、构图、环境
2. 版式说明（40%）：分镜布局、网格排列、阅读方向、比例
3. 文字 UI 规范（15%）：文字覆盖规范
4. 禁止事项（5%）：禁止水印、平台 logo 等
"""
        return user_message

    def derive_all(
        self,
        project_id: int,
        api_key: str
    ) -> list[Script]:
        """
        为项目所有分镜生成图像提示词

        Args:
            project_id: 项目 ID
            api_key: DeepSeek API key

        Returns:
            list[Script]: 更新后的分镜列表
        """
        scripts = (
            db.session.query(Script)
            .filter(Script.project_id == project_id)
            .order_by(Script.shot_index)
            .all()
        )

        derived_scripts = []
        for script in scripts:
            try:
                derived = self.derive_image_prompt(script.id, api_key)
                derived_scripts.append(derived)
            except Exception as e:
                print(f"推导分镜 {script.id} 失败: {e}")
                continue

        return derived_scripts
