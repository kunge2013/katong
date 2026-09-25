# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import re
from typing import NamedTuple


class CleanResult(NamedTuple):
    """清洗结果"""
    text: str
    is_format_cleaned: bool
    is_serial_cleaned: bool
    is_punct_cleaned: bool
    is_shot_cleaned: bool


class TextCleaner:
    """文本清洗器 - 4 步流水线"""

    def clean(self, text: str) -> CleanResult:
        """
        执行完整清洗流水线

        Args:
            text: 原始文本

        Returns:
            CleanResult: 清洗后的文本和状态标记
        """
        # 第 1 步：格式清洗
        text = self.format_clean(text)
        is_format_cleaned = True

        # 第 2 步：串行清洗
        text = self.serial_clean(text)
        is_serial_cleaned = True

        # 第 3 步：标点清洗
        text = self.punct_clean(text)
        is_punct_cleaned = True

        # 第 4 步：分镜清洗（待实现）
        # text = self.shot_clean(text)
        is_shot_cleaned = False  # 暂未实现

        return CleanResult(
            text=text,
            is_format_cleaned=is_format_cleaned,
            is_serial_cleaned=is_serial_cleaned,
            is_punct_cleaned=is_punct_cleaned,
            is_shot_cleaned=is_shot_cleaned
        )

    def format_clean(self, text: str) -> str:
        """
        格式清洗：标准化换行、空格

        - 统一换行符为 \n
        - 移除多余空行（保留最多 2 个连续换行）
        - 移除行首行尾空格
        """
        # 统一换行符
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 移除多余空行（3 个及以上换行 -> 2 个）
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 移除每行首尾空格
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    def serial_clean(self, text: str) -> str:
        """
        串行清洗：移除连载标记

        - 移除 [连载]、[完结] 等标记
        - 移除 第X章、第X回 等章节标题（如果不需要）
        """
        # 移除常见的连载标记
        patterns = [
            r"\[连载\]",
            r"\[完结\]",
            r"\[付费\]",
            r"\[VIP\]",
            r"【连载】",
            r"【完结】",
        ]

        for pattern in patterns:
            text = re.sub(pattern, "", text)

        return text.strip()

    def punct_clean(self, text: str) -> str:
        """
        标点清洗：修正标点

        - 英文标点 -> 中文标点
        - 修正连续标点
        """
        # 英文标点 -> 中文标点
        replacements = {
            ",": "，",
            ".": "。",
            "!": "！",
            "?": "？",
            ":": "：",
            ";": "；",
            "(": "（",
            ")": "）",
        }

        for eng, chn in replacements.items():
            text = text.replace(eng, chn)

        # 修正连续标点（如 。。。 -> 。。）
        text = re.sub(r"。{3,}", "……", text)
        text = re.sub(r"！{2,}", "！", text)
        text = re.sub(r"？{2,}", "？", text)

        return text.strip()

    def shot_clean(self, text: str) -> str:
        """
        分镜清洗：为分镜做准备（待实现）

        - 移除不必要的段落
        - 标准化对话格式
        """
        # TODO: 实现分镜清洗逻辑
        return text
