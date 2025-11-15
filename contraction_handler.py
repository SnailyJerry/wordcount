"""
缩写处理模块 - 智能处理英文缩写
"""
import re
from typing import List


# 标准缩写映射表（拆分为2个词）
STANDARD_CONTRACTIONS = {
    # ========== 代词 + be动词 ==========
    "i'm": ["i", "am"],
    "you're": ["you", "are"],
    "he's": ["he", "is"],  # 注意：he's 也可能是 he has，但 is 更常见
    "she's": ["she", "is"],  # 注意：she's 也可能是 she has，但 is 更常见
    "it's": ["it", "is"],  # 注意：it's 也可能是 it has，但 is 更常见
    "we're": ["we", "are"],
    "they're": ["they", "are"],

    # ========== 代词 + have动词 ==========
    "i've": ["i", "have"],
    "you've": ["you", "have"],
    "we've": ["we", "have"],
    "they've": ["they", "have"],

    # ========== 代词 + will动词 ==========
    "i'll": ["i", "will"],
    "you'll": ["you", "will"],
    "he'll": ["he", "will"],
    "she'll": ["she", "will"],
    "it'll": ["it", "will"],
    "we'll": ["we", "will"],
    "they'll": ["they", "will"],

    # ========== 代词 + would/had动词 ==========
    "i'd": ["i", "would"],
    "you'd": ["you", "would"],
    "he'd": ["he", "would"],
    "she'd": ["she", "would"],
    "it'd": ["it", "would"],
    "we'd": ["we", "would"],
    "they'd": ["they", "would"],

    # ========== 疑问词 + be动词/have动词 ==========
    "who's": ["who", "is"],
    "what's": ["what", "is"],
    "where's": ["where", "is"],
    "when's": ["when", "is"],
    "why's": ["why", "is"],
    "how's": ["how", "is"],
    "there's": ["there", "is"],
    "that's": ["that", "is"],
    "here's": ["here", "is"],

    # ========== 动词 + not ==========
    "don't": ["do", "not"],
    "doesn't": ["does", "not"],
    "didn't": ["did", "not"],
    "can't": ["can", "not"],
    "cannot": ["can", "not"],
    "couldn't": ["could", "not"],
    "won't": ["will", "not"],
    "wouldn't": ["would", "not"],
    "shouldn't": ["should", "not"],
    "mustn't": ["must", "not"],
    "isn't": ["is", "not"],
    "aren't": ["are", "not"],
    "wasn't": ["was", "not"],
    "weren't": ["were", "not"],
    "hasn't": ["has", "not"],
    "haven't": ["have", "not"],
    "hadn't": ["had", "not"],
    "needn't": ["need", "not"],
    "daren't": ["dare", "not"],
    "shan't": ["shall", "not"],

    # ========== 其他常见缩写 ==========
    "let's": ["let", "us"],
    "ma'am": ["madam"],  # 特殊：拆分为1个词
    "o'clock": ["of", "the", "clock"],  # 特殊：拆分为3个词
}


def expand_contractions(text: str) -> str:
    """
    智能展开缩写
    - 标准缩写（如 I'm, you're）拆分为2个词
    - 所有格（如 Uncle's, Sally's）保持为1个词（移除's）
    
    Args:
        text: 输入文本
    
    Returns:
        展开后的文本
    """
    # 步骤1: 展开标准缩写
    for contraction, expansion in STANDARD_CONTRACTIONS.items():
        # 使用单词边界确保完整匹配
        pattern = r'\b' + re.escape(contraction) + r'\b'
        replacement = ' '.join(expansion)
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # 步骤2: 处理所有格（移除's，保持为1个词）
    # 匹配模式：单词 + 's（但不是标准缩写）
    # 例如：Uncle's → Uncle, Sally's → Sally
    text = re.sub(r"\b([a-zA-Z]+)'s\b", r'\1', text)
    
    return text


def extract_words_with_smart_contractions(text: str) -> List[str]:
    """
    使用智能缩写处理提取单词
    
    Args:
        text: 输入文本
    
    Returns:
        单词列表（小写）
    """
    # 先展开缩写
    expanded_text = expand_contractions(text)
    
    # 提取单词
    words = re.findall(r'\b[a-zA-Z]+\b', expanded_text)
    
    # 转为小写
    words_lower = [word.lower() for word in words]
    
    return words_lower


def handle_hyphenated_words(text: str, keep_as_one: bool = True) -> str:
    """
    处理连字符词 (Hyphenated Words)

    规则：连字符词作为单一概念存在时，算作1个词
    例如：well-being, state-of-the-art, twenty-five, mother-in-law

    Args:
        text: 输入文本
        keep_as_one: 是否保持为一个词（默认True）

    Returns:
        处理后的文本
    """
    if keep_as_one:
        # 将连字符替换为下划线，保持为一个token
        # 例如：well-being → well_being
        text = re.sub(r'([a-zA-Z]+)-([a-zA-Z]+)', r'\1_\2', text)
    else:
        # 将连字符替换为空格，拆分为多个词
        # 例如：well-being → well being
        text = re.sub(r'([a-zA-Z]+)-([a-zA-Z]+)', r'\1 \2', text)

    return text


def handle_informal_contractions(text: str) -> str:
    """
    处理非标准缩写/口语缩写 (Informal/Slang Contractions)

    规则：这些通常算作1个词，或者标记为非标准词汇
    例如：gonna, wanna, y'all, gotta, kinda, sorta

    Args:
        text: 输入文本

    Returns:
        处理后的文本（保持原样，不拆分）
    """
    # 非标准缩写映射（可选：展开为标准形式）
    informal_map = {
        "gonna": "going to",
        "wanna": "want to",
        "gotta": "got to",
        "kinda": "kind of",
        "sorta": "sort of",
        "y'all": "you all",
        "ain't": "am not",  # 或 is not, are not, has not, have not
    }

    # 注意：对于词汇量统计，通常保持原样（算1个词）
    # 如果需要展开，可以取消下面的注释
    # for informal, formal in informal_map.items():
    #     text = re.sub(r'\b' + re.escape(informal) + r'\b', formal, text, flags=re.IGNORECASE)

    return text


# ========== 特殊情况处理说明 ==========
"""
以下情况在当前实现中的处理方式：

1. 连字符词 (Hyphenated Words)：
   - 默认：算作1个词（如 well-being）
   - 可通过 handle_hyphenated_words() 调整

2. 复合词 (Compound Nouns)：
   - 写成一个词的：算作1个词（如 toothbrush）
   - 分开写的：算作多个词（如 ice cream → 2个词）
   - 注意：这需要语义分析，当前不做特殊处理

3. 短语动词 (Phrasal Verbs)：
   - 当前：算作多个词（如 look up → 2个词）
   - 注意：需要语义分析才能识别，当前不做特殊处理

4. 习语和固定短语 (Idioms)：
   - 当前：算作多个词（如 kick the bucket → 3个词）
   - 注意：需要语义分析才能识别，当前不做特殊处理

5. 专有名词 (Proper Nouns)：
   - 当前：算作多个词（如 New York → 2个词）
   - 注意：需要命名实体识别，当前不做特殊处理

6. 非标准缩写 (Informal Contractions)：
   - 当前：算作1个词（如 gonna, wanna）
   - 可通过 handle_informal_contractions() 调整

建议：
- 对于儿童英语学习材料，当前的处理方式（简单拆分）是合理的
- 如果需要更精确的词汇量统计，可以考虑引入NLP库（如spaCy）进行语义分析
"""


def test_contraction_handler():
    """
    测试缩写处理功能
    """
    test_cases = [
        "I'm happy",
        "You're right",
        "It's a cat",
        "Uncle's story",
        "Sally's coat",
        "Don't worry",
        "Can't wait",
        "I'll go",
        "They've arrived",
        "Who's there?",
        "What's that?",
        "Let's go!",
        "There's a book",
    ]

    print("=" * 80)
    print("缩写处理测试")
    print("=" * 80)

    for test in test_cases:
        expanded = expand_contractions(test)
        words = extract_words_with_smart_contractions(test)
        print(f"\n原文: {test}")
        print(f"展开: {expanded}")
        print(f"单词: {words} (共{len(words)}个)")


if __name__ == "__main__":
    test_contraction_handler()

