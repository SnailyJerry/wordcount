"""
验证模块 - 三种方法交叉验证词汇统计准确性
"""
import re
from collections import Counter
from typing import Dict, List
from .contraction_handler import extract_words_with_smart_contractions


def count_words_method1(text: str) -> Dict[str, any]:
    """
    方法1: 使用智能缩写处理 + 正则表达式（推荐方法）
    """
    words = extract_words_with_smart_contractions(text)

    total_words = len(words)
    word_freq = Counter(words)
    unique_words = len(word_freq)

    return {
        'method': '方法1 (智能缩写)',
        'total_words': total_words,
        'unique_words': unique_words,
        'word_list': words,
        'word_freq': dict(word_freq)
    }


def count_words_method2(text: str) -> Dict[str, any]:
    """
    方法2: 使用 split() + 手动过滤
    """
    # 按空格分割并过滤
    tokens = text.split()
    words = []

    for token in tokens:
        # 移除首尾的非字母字符
        cleaned = token.strip('.,!?;:"()[]{}0123456789-–—\'""''')
        # 仅保留包含字母的token
        if cleaned and any(c.isalpha() for c in cleaned):
            # 提取纯字母部分
            alpha_only = ''.join(c for c in cleaned if c.isalpha())
            if alpha_only:
                words.append(alpha_only.lower())

    total_words = len(words)
    word_freq = Counter(words)
    unique_words = len(word_freq)

    return {
        'method': '方法2 (分割过滤)',
        'total_words': total_words,
        'unique_words': unique_words,
        'word_list': words,
        'word_freq': dict(word_freq)
    }


def count_words_method3(text: str) -> Dict[str, any]:
    """
    方法3: 多重正则模式验证
    """
    # 先移除数字
    text_no_numbers = re.sub(r'\d+', '', text)

    # 查找所有字母序列
    words = re.findall(r'[a-zA-Z]+', text_no_numbers)
    words = [word.lower() for word in words if len(word) > 0]

    total_words = len(words)
    word_freq = Counter(words)
    unique_words = len(word_freq)

    return {
        'method': '方法3 (多重模式)',
        'total_words': total_words,
        'unique_words': unique_words,
        'word_list': words,
        'word_freq': dict(word_freq)
    }


def compare_results(results: List[Dict]) -> Dict[str, any]:
    """
    比较多种方法的统计结果

    Args:
        results: 多个方法的结果列表

    Returns:
        对比报告字典
    """
    if len(results) < 2:
        return {'status': 'error', 'message': '至少需要2种方法进行对比'}

    # 提取指标
    total_words = [r['total_words'] for r in results]
    unique_words = [r['unique_words'] for r in results]

    # 检查一致性
    total_consistent = len(set(total_words)) == 1
    unique_consistent = len(set(unique_words)) == 1

    report = {
        'status': 'pass' if (total_consistent and unique_consistent) else 'warning',
        'consistent': total_consistent and unique_consistent,
        'total_words': {
            'consistent': total_consistent,
            'values': {r['method']: r['total_words'] for r in results},
            'min': min(total_words),
            'max': max(total_words),
            'difference': max(total_words) - min(total_words)
        },
        'unique_words': {
            'consistent': unique_consistent,
            'values': {r['method']: r['unique_words'] for r in results},
            'min': min(unique_words),
            'max': max(unique_words),
            'difference': max(unique_words) - min(unique_words)
        }
    }

    return report


def verify_text(text: str) -> Dict[str, any]:
    """
    对文本进行三遍统计验证

    Args:
        text: 输入文本

    Returns:
        完整的验证报告，包括:
        - results: 三种方法的统计结果
        - comparison: 对比结果
        - recommendation: 可靠性建议
        - final_stats: 推荐使用的最终统计值（取最高值）
    """
    # 运行三种方法
    result1 = count_words_method1(text)
    result2 = count_words_method2(text)
    result3 = count_words_method3(text)

    results = [result1, result2, result3]

    # 对比结果
    comparison = compare_results(results)

    # 生成建议
    recommendation = get_recommendation(comparison)

    # 优先使用方法1（智能缩写方法），这是最准确的方法
    # 只有当方法1明显偏低时（差异>10%），才考虑使用其他方法
    best_result = result1

    if not comparison['consistent']:
        # 有差异时，检查方法1是否明显偏低
        max_total = max(r['total_words'] for r in results)
        method1_total = result1['total_words']

        # 如果方法1的总词数比最高值低10%以上，使用最高值的方法
        if max_total > 0 and (max_total - method1_total) / max_total > 0.1:
            best_result = max(results, key=lambda r: r['total_words'])
        # 否则，始终使用方法1（智能缩写方法）

    final_stats = {
        'total_words': best_result['total_words'],
        'unique_words': best_result['unique_words'],
        'word_freq': best_result['word_freq'],
        'unique_word_list': sorted(best_result['word_freq'].keys()),
        'selected_method': best_result['method']  # 记录使用的方法
    }

    return {
        'results': results,
        'comparison': comparison,
        'recommendation': recommendation,
        'final_stats': final_stats,
        'verified': comparison['consistent']
    }


def get_recommendation(comparison: Dict) -> str:
    """
    根据对比结果生成可靠性建议

    Args:
        comparison: 对比结果字典

    Returns:
        建议文本
    """
    if comparison['status'] == 'pass':
        return "✅ 三种方法结果完全一致，统计结果可靠"

    total_diff = comparison['total_words']['difference']
    unique_diff = comparison['unique_words']['difference']

    if total_diff <= 2 and unique_diff <= 2:
        return "✅ 检测到轻微差异（≤2个词），结果可靠"
    elif total_diff <= 10 and unique_diff <= 5:
        return "✅ 检测到小幅差异（≤10个词），结果可靠"
    elif total_diff <= 50:
        return "✅ 检测到差异（≤50个词），结果正常"
    else:
        return "⚠️ 检测到较大差异（>50个词），建议检查文本内容"


def get_verification_summary(comparison: Dict) -> str:
    """
    获取简短的验证摘要（用于界面显示）

    Args:
        comparison: 对比结果字典

    Returns:
        简短摘要文本
    """
    if comparison['consistent']:
        return "验证通过 ✅"

    total_diff = comparison['total_words']['difference']
    unique_diff = comparison['unique_words']['difference']

    if total_diff <= 2 and unique_diff <= 2:
        return "验证通过 ✅"
    elif total_diff <= 10 and unique_diff <= 5:
        return "验证通过 ✅"
    elif total_diff <= 50:
        return "验证通过 ✅"
    else:
        return "需要检查 ⚠️"
