# [AGC:FILE] tool=Cc author=fangkun date=2026-09-25

import pytest
from cinegacha.services.text_cleaner import TextCleaner


@pytest.fixture
def cleaner():
    """创建清洗器实例"""
    return TextCleaner()


def test_format_clean(cleaner):
    """格式清洗：标准化换行"""
    text = "第一行\r\n第二行\n\n\n第三行"
    result = cleaner.format_clean(text)

    assert "\r" not in result
    # 原始 3 个连续换行 -> 2 个，加上正常的换行
    assert "\n\n\n" not in result  # 不应该有 3 个连续换行
    assert "第一行" in result
    assert "第三行" in result


def test_serial_clean(cleaner):
    """串行清洗：移除连载标记"""
    text = "这是小说内容 [连载] [VIP] ..."
    result = cleaner.serial_clean(text)

    assert "[连载]" not in result
    assert "[VIP]" not in result
    assert "这是小说内容" in result


def test_punct_clean(cleaner):
    """标点清洗：英文 -> 中文"""
    text = "Hello, world! How are you?"
    result = cleaner.punct_clean(text)

    assert "，" in result
    assert "！" in result
    assert "," not in result
    assert "!" not in result


def test_punct_clean_consecutive(cleaner):
    """标点清洗：连续标点"""
    text = "什么！！！"
    result = cleaner.punct_clean(text)

    assert result == "什么！"


def test_full_clean_pipeline(cleaner):
    """完整清洗流水线"""
    text = "小说内容 [连载]\r\n\r\n\r\nHello, world!..."

    result = cleaner.clean(text)

    assert result.is_format_cleaned is True
    assert result.is_serial_cleaned is True
    assert result.is_punct_cleaned is True
    assert result.is_shot_cleaned is False  # 暂未实现

    # 验证清洗效果
    assert "[连载]" not in result.text
    assert "\r" not in result.text
    assert "，" in result.text


def test_clean_chinese_text(cleaner):
    """清洗中文小说文本"""
    text = """
    第一章 开始

    [连载]
    明溪走进祠堂,月光洒下...
    她想起了过去的日子!!!

    """

    result = cleaner.clean(text)

    assert "[连载]" not in result.text
    assert "，" in result.text
    assert "。" in result.text or "！" in result.text
    assert result.is_format_cleaned is True
