"""
TXT导出模块 - 生成词汇统计报告
"""
from datetime import datetime
from typing import Dict


def generate_txt_report(results: Dict, book_name: str = "未命名书籍") -> str:
    """
    生成TXT格式的词汇统计报告
    
    Args:
        results: 处理结果字典（来自process_book_files）
        book_name: 书籍名称
        
    Returns:
        TXT格式的报告内容
    """
    individual_results = results['individual_results']
    summary = results['summary']
    
    # 生成报告
    lines = []
    
    # 标题
    lines.append("=" * 80)
    lines.append(f"📚 英语词汇量统计报告")
    lines.append("=" * 80)
    lines.append(f"")
    lines.append(f"书籍名称: {book_name}")
    lines.append(f"统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"统计文件数: {summary['total_files']}")
    lines.append(f"验证状态: {'✅ 全部通过' if summary['all_verified'] else '⚠️ 部分未通过'}")
    lines.append(f"")
    
    # 汇总统计
    lines.append("=" * 80)
    lines.append("📊 汇总统计")
    lines.append("=" * 80)
    lines.append(f"")
    
    # 表格形式展示
    lines.append(f"{'文件类型':<15} {'总词数':<12} {'唯一词数':<12} {'验证状态':<15}")
    lines.append("-" * 80)
    
    for file_type in ['1双语', '2原文', '3外教']:
        if file_type in individual_results:
            stats = individual_results[file_type]
            verification = stats.get('verification_status', '未验证')

            # 如果是2原文，添加说明
            total_words_str = str(stats['total_words'])
            if file_type == '2原文' and 'original_total_words' in stats:
                total_words_str = f"{stats['total_words']} (×3)"

            lines.append(f"{file_type:<15} {total_words_str:<12} {stats['unique_words']:<12} {verification:<15}")
    
    lines.append(f"")
    
    # 详细统计（每种类型）
    for file_type in ['1双语', '2原文', '3外教']:
        if file_type not in individual_results:
            continue
            
        stats = individual_results[file_type]
        
        lines.append("=" * 80)
        lines.append(f"📄 {file_type} - 详细统计")
        lines.append("=" * 80)
        lines.append(f"")
        lines.append(f"文件名: {stats['filename']}")

        # 如果是2原文，显示原始值和乘以3后的值
        if file_type == '2原文' and 'original_total_words' in stats:
            lines.append(f"总词数: {stats['total_words']} (原始: {stats['original_total_words']} × 3)")
            lines.append(f"  说明: 原文高效磨耳需要重复听3遍，因此总词数×3")
        else:
            lines.append(f"总词数: {stats['total_words']}")

        lines.append(f"唯一词数: {stats['unique_words']}")
        lines.append(f"")
        
        # 验证详情
        lines.append(f"🔍 验证详情:")
        lines.append(f"  验证状态: {stats.get('verification_status', '未验证')}")
        lines.append(f"  验证结果: {stats.get('verification_detail', '无详情')}")
        
        # 如果有验证对比信息
        if 'verification_comparison' in stats:
            comp = stats['verification_comparison']
            if not comp.get('consistent', True):
                lines.append(f"")
                lines.append(f"  ⚠️ 验证差异详情:")
                total_diff = comp['total_words']['difference']
                unique_diff = comp['unique_words']['difference']
                lines.append(f"    总词数差异: {total_diff}")
                lines.append(f"    唯一词数差异: {unique_diff}")
        
        lines.append(f"")
        
        # 唯一词列表
        lines.append(f"📝 唯一词列表 (共 {stats['unique_words']} 个):")
        lines.append(f"")
        
        unique_words = stats.get('unique_word_list', [])
        
        # 按字母顺序排列，每行10个单词
        for i in range(0, len(unique_words), 10):
            batch = unique_words[i:i+10]
            lines.append(f"  {', '.join(batch)}")
        
        lines.append(f"")
        
        # 词频统计（Top 20）
        if 'word_freq' in stats:
            word_freq = stats['word_freq']
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            top_20 = sorted_words[:20]
            
            lines.append(f"🔝 高频词汇 (Top 20):")
            lines.append(f"")
            lines.append(f"{'排名':<6} {'单词':<20} {'出现次数':<10}")
            lines.append("-" * 40)
            
            for idx, (word, count) in enumerate(top_20, 1):
                lines.append(f"{idx:<6} {word:<20} {count:<10}")
            
            lines.append(f"")
    
    # 页脚
    lines.append("=" * 80)
    lines.append("📌 说明:")
    lines.append("  - 总词数: 文本中所有英文单词的数量（含重复）")
    lines.append("  - 唯一词数: 去重后的不同单词数量")
    lines.append("  - 验证状态: 使用三种方法交叉验证统计准确性")
    lines.append("  - 单词识别: 仅统计英文字母组成的单词，自动转为小写处理")
    lines.append("  - 2原文特殊处理: 总词数自动×3（因为需要重复听3遍）")
    lines.append("=" * 80)
    lines.append(f"")
    lines.append(f"报告生成完成 ✅")
    lines.append(f"")
    
    return '\n'.join(lines)


def get_download_filename(book_name: str = "未命名书籍") -> str:
    """
    生成下载文件名
    
    Args:
        book_name: 书籍名称
        
    Returns:
        文件名
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # 清理书籍名称中的特殊字符
    clean_name = book_name.replace(' ', '_').replace('/', '_')
    return f"词汇统计报告_{clean_name}_{timestamp}.txt"

