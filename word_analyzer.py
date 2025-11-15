"""
词汇分析模块 - 统计英文词汇（三遍验证）
"""
import re
from collections import Counter
from typing import Dict, List
from .verify import verify_text, get_verification_summary


def analyze_text(text: str, enable_verification: bool = True) -> Dict:
    """
    分析文本中的英文词汇（支持三遍验证）

    Args:
        text: 输入文本
        enable_verification: 是否启用三遍统计验证（默认True）

    Returns:
        包含统计数据的字典:
        - total_words: 总词数
        - unique_words: 唯一词数
        - unique_word_list: 唯一词列表（按字母排序）
        - word_freq: 词频字典
        - verified: 是否通过验证（仅当enable_verification=True时）
        - verification_status: 验证状态摘要
        - verification_detail: 详细验证信息
    """
    if enable_verification:
        # 使用三遍统计验证
        verification_report = verify_text(text)

        # 提取最终统计结果
        stats = verification_report['final_stats']

        # 添加验证信息
        stats['verified'] = verification_report['verified']
        stats['verification_status'] = get_verification_summary(verification_report['comparison'])
        stats['verification_detail'] = verification_report['recommendation']
        stats['verification_comparison'] = verification_report['comparison']

        return stats
    else:
        # 单次统计（快速模式）
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        words_lower = [word.lower() for word in words]

        total_words = len(words_lower)
        word_freq = Counter(words_lower)
        unique_words = len(word_freq)
        unique_word_list = sorted(word_freq.keys())

        return {
            'total_words': total_words,
            'unique_words': unique_words,
            'unique_word_list': unique_word_list,
            'word_freq': dict(word_freq),
            'verified': None,
            'verification_status': '未验证（快速模式）',
            'verification_detail': '未启用验证'
        }


def export_unique_words_csv(unique_word_list: List[str], output_path: str):
    """
    将唯一词列表导出为CSV文件

    Args:
        unique_word_list: 唯一词列表
        output_path: 输出文件路径
    """
    import csv
    import os

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['序号', '单词'])  # 表头
        for idx, word in enumerate(unique_word_list, 1):
            writer.writerow([idx, word])


def export_statistics_csv(stats: Dict, output_path: str):
    """
    将统计摘要导出为CSV文件

    Args:
        stats: 统计数据字典
        output_path: 输出文件路径
    """
    import csv
    import os

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['统计项', '数值'])
        writer.writerow(['总词数', stats['total_words']])
        writer.writerow(['唯一词数', stats['unique_words']])

        # 添加验证信息
        if 'verification_status' in stats:
            writer.writerow([''])
            writer.writerow(['验证状态', stats['verification_status']])
            if 'verification_detail' in stats:
                writer.writerow(['验证详情', stats['verification_detail']])
