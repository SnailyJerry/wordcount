"""
书籍文件处理模块 - 处理三种类型的文本文件
"""
import re
from typing import Dict, Tuple, Optional
from .word_analyzer import analyze_text
from .text_cleaner import extract_english_only


def identify_file_type(filename: str) -> Optional[str]:
    """
    根据文件名识别文件类型
    
    Args:
        filename: 文件名
        
    Returns:
        文件类型 ('1双语', '2原文', '3外教') 或 None
    """
    filename_lower = filename.lower()
    
    if filename.startswith('1双语-') or '双语' in filename:
        return '1双语'
    elif filename.startswith('2原文-') or '原文' in filename:
        return '2原文'
    elif filename.startswith('3外教-') or '外教' in filename:
        return '3外教'
    else:
        return None


def preprocess_text(text: str, file_type: str) -> str:
    """
    根据文件类型预处理文本
    
    Args:
        text: 原始文本
        file_type: 文件类型 ('1双语', '2原文', '3外教')
        
    Returns:
        预处理后的文本
    """
    if file_type == '1双语':
        # 双语文本：移除中文（包括中文标点和全角字符）
        # Unicode范围：
        # \u4e00-\u9fff: 中文字符
        # \u3000-\u303f: CJK标点符号
        # \uff00-\uffef: 全角字符
        text = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+', ' ', text)
        
    elif file_type == '2原文':
        # 原文：纯英文，无需特殊处理
        pass
        
    elif file_type == '3外教':
        # 外教对话：移除说话人标记 + Markdown标记 + 中文
        # 1. 移除说话人标记（如 **Sally:**、**Pete:** 等）
        # 匹配模式：**任意单词: （注意：只有开头的**，后面没有**）
        text = re.sub(r'\*\*[A-Za-z]+:', '', text)

        # 2. 移除剩余的Markdown粗体标记 **text**
        text = re.sub(r'\*\*', '', text)

        # 3. 移除中文（包括中文标点和全角字符）
        text = re.sub(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]+', ' ', text)
    
    # 统一清理多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def analyze_book_file(text: str, file_type: str, filename: str, enable_verification: bool = True) -> Dict:
    """
    分析单个书籍文件的词汇量

    Args:
        text: 文件文本内容
        file_type: 文件类型
        filename: 文件名
        enable_verification: 是否启用三遍验证

    Returns:
        包含统计结果的字典

    注意：
        - 2原文（原文高效磨耳）的总词数会自动乘以3（因为需要重复听3遍）
        - 唯一词数保持不变
    """
    # 1. 预处理文本
    cleaned_text = preprocess_text(text, file_type)

    # 2. 使用三遍验证统计词汇
    stats = analyze_text(cleaned_text, enable_verification=enable_verification)

    # 3. 特殊处理：2原文（原文高效磨耳）的总词数乘以3
    if file_type == '2原文':
        original_total = stats['total_words']
        stats['total_words'] = original_total * 3
        stats['original_total_words'] = original_total  # 保存原始值供参考
        stats['multiplier'] = 3  # 记录倍数

    # 4. 添加文件信息
    stats['file_type'] = file_type
    stats['filename'] = filename
    stats['cleaned_text'] = cleaned_text
    stats['cleaned_text_preview'] = cleaned_text[:300] + '...' if len(cleaned_text) > 300 else cleaned_text

    return stats


def validate_uploaded_files(files: list) -> Tuple[bool, list, Dict]:
    """
    验证上传的文件是否符合要求
    
    Args:
        files: 上传的文件列表
        
    Returns:
        (是否有效, 缺失的类型列表, 文件类型映射字典)
    """
    file_types = {}
    
    for file in files:
        file_type = identify_file_type(file.name)
        if file_type:
            file_types[file_type] = file
    
    # 检查是否包含3种类型
    required = ['1双语', '2原文', '3外教']
    missing = [t for t in required if t not in file_types]
    
    return len(missing) == 0, missing, file_types


def process_book_files(uploaded_files: Dict, enable_verification: bool = True) -> Dict:
    """
    处理一本书的3个文件
    
    Args:
        uploaded_files: 文件类型到文件对象的映射 {'1双语': file, '2原文': file, '3外教': file}
        enable_verification: 是否启用三遍验证
        
    Returns:
        处理结果字典，包含每个文件的统计结果和汇总信息
    """
    results = {}
    
    for file_type in ['1双语', '2原文', '3外教']:
        if file_type in uploaded_files:
            file = uploaded_files[file_type]
            
            # 读取文件内容
            text = file.read().decode('utf-8')
            
            # 分析词汇量
            stats = analyze_book_file(text, file_type, file.name, enable_verification)
            
            results[file_type] = stats
    
    # 生成汇总信息
    summary = generate_summary(results)
    
    return {
        'individual_results': results,
        'summary': summary
    }


def generate_summary(results: Dict) -> Dict:
    """
    生成汇总报告

    Args:
        results: 各文件的统计结果

    Returns:
        汇总信息字典
    """
    # 检查所有文件是否都通过验证
    # 验证通过的条件：验证状态包含"✅"或"验证通过"
    def is_verified(result):
        status = result.get('verification_status', '')
        return '✅' in status or '验证通过' in status

    summary = {
        'total_files': len(results),
        'all_verified': all(is_verified(r) for r in results.values()),
        'total_words_comparison': {k: v['total_words'] for k, v in results.items()},
        'unique_words_comparison': {k: v['unique_words'] for k, v in results.items()},
    }

    return summary

