# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import os
from typing import Optional
from cinegacha import db
from cinegacha.models.script import Script
from cinegacha.models.project import Project


class GenerationService:
    """图像生成服务 - Stage 6"""

    def __init__(self):
        self.output_dir = "Output"

    def generate_image(
        self,
        script_id: int,
        image_prompt: str,
        project_id: int
    ) -> str:
        """
        生成单张图像

        Args:
            script_id: 分镜 ID
            image_prompt: 图像提示词
            project_id: 项目 ID

        Returns:
            str: 生成的图像本地路径
        """
        # 创建输出目录
        output_path = os.path.join(
            self.output_dir,
            str(project_id),
            "images"
        )
        os.makedirs(output_path, exist_ok=True)

        # 调用 GRSai API (实际实现时替换为真实 API 调用)
        image_filename = f"shot_{script_id}.png"
        local_path = os.path.join(output_path, image_filename)

        # TODO: 实际调用 nano-banana-2 via GRSai
        # 这里只是占位，实际需要 HTTP 请求
        # response = httpx.post(GRSAI_ENDPOINT, json={...})

        # 返回本地路径
        return local_path

    def generate_all(
        self,
        project_id: int
    ) -> list[dict]:
        """
        批量生成项目所有分镜的图像

        Args:
            project_id: 项目 ID

        Returns:
            list[dict]: 生成结果列表
        """
        # 获取项目所有分镜
        scripts = (
            db.session.query(Script)
            .filter(Script.project_id == project_id)
            .order_by(Script.shot_index)
            .all()
        )

        results = []
        for script in scripts:
            if not script.image_prompt:
                results.append({
                    "script_id": script.id,
                    "status": "skipped",
                    "reason": "no image_prompt"
                })
                continue

            try:
                local_path = self.generate_image(
                    script_id=script.id,
                    image_prompt=script.image_prompt,
                    project_id=project_id
                )

                # 更新数据库
                script.main_image = local_path
                db.session.commit()

                results.append({
                    "script_id": script.id,
                    "status": "success",
                    "image_path": local_path
                })
            except Exception as e:
                results.append({
                    "script_id": script.id,
                    "status": "failed",
                    "error": str(e)
                })

        return results
