"""
文本清理模块 - 剔除中文，只保留英文内容
"""
import re


def remove_chinese(text: str, keep_punctuation: bool = True) -> str:
    """
    剔除文本中的中文字符，只保留英文内容

    Args:
        text: 输入文本
        keep_punctuation: 是否保留英文标点符号（默认True）

    Returns:
        只包含英文的文本
    """
    if keep_punctuation:
        # 保留英文字母、数字、空格、常见英文标点
        # 移除中文字符（包括中文标点）
        pattern = r'[^\x00-\x7F]+'  # 移除所有非ASCII字符（包括中文）
        cleaned = re.sub(pattern, ' ', text)
    else:
        # 只保留英文字母、数字和空格
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # 清理多余空格
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()

    return cleaned


def extract_english_only(text: str, preserve_structure: bool = False) -> str:
    """
    提取文本中的纯英文内容（更智能的版本）

    Args:
        text: 输入文本
        preserve_structure: 是否保留原文结构（换行等）

    Returns:
        只包含英文的文本
    """
    if preserve_structure:
        # 按行处理，保留换行结构
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            # 移除中文字符
            cleaned_line = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+', '', line)
            # 清理多余空格
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()

            # 只保留有内容的行
            if cleaned_line:
                cleaned_lines.append(cleaned_line)

        return '\n'.join(cleaned_lines)
    else:
        # 移除所有中文字符（包括中文标点）
        # Unicode范围：\u4e00-\u9fff (中文), \u3000-\u303f (CJK标点), \uff00-\uffef (全角字符)
        cleaned = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+', ' ', text)

        # 清理多余空格
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()

        return cleaned


def clean_text_advanced(text: str, options: dict = None) -> str:
    """
    高级文本清理（可自定义选项）

    Args:
        text: 输入文本
        options: 清理选项字典
            - remove_chinese: 移除中文（默认True）
            - keep_numbers: 保留数字（默认True）
            - keep_punctuation: 保留标点（默认True）
            - preserve_newlines: 保留换行（默认False）

    Returns:
        清理后的文本
    """
    if options is None:
        options = {}

    remove_chinese = options.get('remove_chinese', True)
    keep_numbers = options.get('keep_numbers', True)
    keep_punctuation = options.get('keep_punctuation', True)
    preserve_newlines = options.get('preserve_newlines', False)

    result = text

    # 移除中文
    if remove_chinese:
        result = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+', ' ', result)

    # 构建保留字符的正则
    if keep_numbers and keep_punctuation:
        # 保留英文字母、数字、标点和空格
        result = re.sub(r'[^\x00-\x7F]+', ' ', result)
    elif keep_numbers:
        # 只保留英文字母、数字和空格
        result = re.sub(r'[^a-zA-Z0-9\s\n]', ' ', result)
    elif keep_punctuation:
        # 只保留英文字母、标点和空格
        result = re.sub(r'[^a-zA-Z\s\n.!?,;:\'"()-]', ' ', result)
    else:
        # 只保留英文字母和空格
        result = re.sub(r'[^a-zA-Z\s\n]', ' ', result)

    # 处理空格和换行
    if preserve_newlines:
        # 保留换行，但清理每行的多余空格
        lines = result.split('\n')
        result = '\n'.join(re.sub(r' +', ' ', line).strip() for line in lines)
    else:
        # 统一清理空格
        result = re.sub(r'\s+', ' ', result)

    return result.strip()


def get_text_statistics(original: str, cleaned: str) -> dict:
    """
    获取清理前后的文本统计

    Args:
        original: 原始文本
        cleaned: 清理后文本

    Returns:
        统计信息字典
    """
    return {
        'original_length': len(original),
        'cleaned_length': len(cleaned),
        'removed_chars': len(original) - len(cleaned),
        'removal_rate': f"{((len(original) - len(cleaned)) / len(original) * 100):.2f}%" if len(original) > 0 else "0%"
    }
