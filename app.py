"""
英语词汇量统计工具 - Streamlit应用
支持三种文件类型：1双语、2原文、3外教
基于三遍验证技术，确保统计准确性
"""
import streamlit as st
from utils.book_processor import validate_uploaded_files, process_book_files
from utils.txt_exporter import generate_txt_report, get_download_filename


def main():
    # 页面配置
    st.set_page_config(
        page_title="英语词汇量统计工具",
        page_icon="📚",
        layout="wide"
    )
    
    # 标题
    st.title("📚 英语词汇量统计工具")
    st.markdown("**三类文本专业版** - 基于三遍验证技术，确保统计准确性")
    st.markdown("---")
    
    # 侧边栏说明
    with st.sidebar:
        st.header("📖 使用说明")
        st.markdown("""
        ### 上传要求
        
        请上传一本书的 **3个文件**：
        
        1. **1双语-xxx.txt** - 中英文混合内容
        2. **2原文-xxx.txt** - 纯英文原文
        3. **3外教-xxx.md** - 双语对话
        
        ### 统计说明

        - ✅ **自动过滤中文**（1双语、3外教）
        - ✅ **三遍验证**确保准确性
        - ✅ **智能识别**文件类型
        - ✅ **详细报告**TXT格式下载
        - ⭐ **2原文自动×3**（重复听3遍）
        
        ### 技术特点
        
        - 使用三种方法交叉验证
        - Unicode精确过滤中文
        - Markdown标记智能处理
        - 只统计纯英文单词
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ 高级选项")
        
        enable_verification = st.checkbox(
            "启用三遍验证",
            value=True,
            help="使用三种方法交叉验证统计准确性（推荐）"
        )
        
        show_preview = st.checkbox(
            "显示清理后文本预览",
            value=False,
            help="查看过滤中文后的英文文本"
        )
    
    # 主界面
    st.header("📤 上传文件")
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "请选择3个文件（1双语、2原文、3外教）",
        type=['txt', 'md'],
        accept_multiple_files=True,
        help="支持 .txt 和 .md 格式"
    )
    
    if uploaded_files:
        # 验证上传的文件
        is_valid, missing, file_types = validate_uploaded_files(uploaded_files)
        
        # 显示上传状态
        st.subheader("📋 上传文件状态")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if '1双语' in file_types:
                st.success(f"✅ 1双语")
                st.caption(file_types['1双语'].name)
            else:
                st.error("❌ 1双语 - 缺失")
        
        with col2:
            if '2原文' in file_types:
                st.success(f"✅ 2原文")
                st.caption(file_types['2原文'].name)
            else:
                st.error("❌ 2原文 - 缺失")
        
        with col3:
            if '3外教' in file_types:
                st.success(f"✅ 3外教")
                st.caption(file_types['3外教'].name)
            else:
                st.error("❌ 3外教 - 缺失")
        
        # 如果文件不完整，显示提示
        if not is_valid:
            st.warning(f"⚠️ 请上传完整的3个文件。当前缺失: {', '.join(missing)}")
            return
        
        st.success("✅ 文件上传完整！")
        
        # 开始统计按钮
        st.markdown("---")
        
        if st.button("🚀 开始统计（三遍验证）", type="primary", use_container_width=True):
            with st.spinner("正在统计词汇量..."):
                # 处理文件
                results = process_book_files(file_types, enable_verification=enable_verification)
                
                # 保存结果到session state
                st.session_state['results'] = results
                st.session_state['file_types'] = file_types
            
            st.success("✅ 统计完成！")
    
    # 显示结果
    if 'results' in st.session_state:
        results = st.session_state['results']
        individual_results = results['individual_results']
        summary = results['summary']
        
        st.markdown("---")
        st.header("📊 统计结果")
        
        # 汇总信息
        st.subheader("📈 汇总对比")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("统计文件数", summary['total_files'])
        
        with col2:
            total_all = sum(summary['total_words_comparison'].values())
            st.metric("总词数（合计）", total_all)
        
        with col3:
            # 注意：唯一词数不能简单相加（有重复）
            st.metric("验证状态", "✅ 全部通过" if summary['all_verified'] else "⚠️ 部分未通过")
        
        with col4:
            st.metric("统计方法", "三遍验证" if enable_verification else "快速模式")
        
        # 详细结果（每种类型）
        st.markdown("---")
        st.subheader("📄 详细统计")
        
        for file_type in ['1双语', '2原文', '3外教']:
            if file_type not in individual_results:
                continue
            
            stats = individual_results[file_type]
            
            with st.expander(f"**{file_type}** - {stats['filename']}", expanded=True):
                # 统计指标
                col1, col2, col3 = st.columns(3)

                with col1:
                    # 如果是2原文，显示乘以3的说明
                    if file_type == '2原文' and 'original_total_words' in stats:
                        st.metric(
                            "📊 总词数",
                            stats['total_words'],
                            delta=f"原始: {stats['original_total_words']} × 3",
                            help="原文高效磨耳需要重复听3遍，因此总词数×3"
                        )
                    else:
                        st.metric("📊 总词数", stats['total_words'])

                with col2:
                    st.metric("🔤 唯一词数", stats['unique_words'])

                with col3:
                    verification_status = stats.get('verification_status', '未验证')
                    st.metric("✅ 验证状态", verification_status)
                
                # 验证详情
                if enable_verification:
                    verification_detail = stats.get('verification_detail', '无详情')
                    
                    if '✅' in verification_detail:
                        st.success(f"🔍 {verification_detail}")
                    elif '⚠️' in verification_detail:
                        st.warning(f"🔍 {verification_detail}")
                    else:
                        st.info(f"🔍 {verification_detail}")
                
                # 高频词（Top 10）
                if 'word_freq' in stats:
                    word_freq = stats['word_freq']
                    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                    top_10 = sorted_words[:10]
                    
                    st.markdown("**🔝 Top 10 高频词:**")
                    top_10_str = ', '.join([f"{word}({count})" for word, count in top_10])
                    st.caption(top_10_str)
                
                # 清理后文本预览
                if show_preview and 'cleaned_text_preview' in stats:
                    st.markdown("**👁️ 清理后文本预览:**")
                    st.text_area(
                        "预览",
                        stats['cleaned_text_preview'],
                        height=150,
                        key=f"preview_{file_type}",
                        label_visibility="collapsed"
                    )
        
        # 下载报告
        st.markdown("---")
        st.subheader("📥 下载报告")
        
        # 提取书籍名称（从文件名）
        book_name = "未命名书籍"
        if '2原文' in st.session_state.get('file_types', {}):
            filename = st.session_state['file_types']['2原文'].name
            # 提取书名（去掉前缀和后缀）
            book_name = filename.replace('2原文-', '').replace('_原文', '').replace('.txt', '')
        
        # 生成TXT报告
        txt_report = generate_txt_report(results, book_name)
        download_filename = get_download_filename(book_name)
        
        st.download_button(
            label="📥 下载TXT报告",
            data=txt_report,
            file_name=download_filename,
            mime="text/plain",
            type="primary",
            use_container_width=True
        )
        
        st.caption(f"报告文件名: {download_filename}")


if __name__ == "__main__":
    main()

