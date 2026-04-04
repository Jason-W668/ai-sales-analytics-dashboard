"""
国际化 (i18n) 模块

标准化语言包加载器，支持：
- BCP 47 语言代码 (en, zh-CN, zh-TW, ja, ko, fr...)
- JSON 语言包文件
- 嵌套 key + 点分访问: t("charts.sales_trend")
- 字符串插值: t("charts.top_products", n=10)
- 自动回退: 当前语言 → en → [key]
- 运行时语言包自动发现

语言包目录: locales/
  ├── en.json
  ├── zh-CN.json
  └── ...
"""

import os
import json
import streamlit as st
from typing import Any, Dict, List, Optional
from functools import reduce


# ======================== 常量 ========================

# 语言包目录（相对于项目根目录）
_LOCALES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "locales",
)

# 默认/回退语言
_FALLBACK_LOCALE = "en"


# ======================== 加载语言包 ========================

@st.cache_data
def _load_locale_file(filepath: str) -> dict:
    """加载单个语言包 JSON 文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def _discover_locales() -> Dict[str, dict]:
    """
    自动发现 locales/ 目录下所有语言包
    返回: { "en": { "_meta": {...}, ... }, "zh-CN": {...}, ... }
    """
    locales = {}

    if not os.path.isdir(_LOCALES_DIR):
        st.error(f"❌ Locales directory not found: {_LOCALES_DIR}")
        return locales

    for filename in sorted(os.listdir(_LOCALES_DIR)):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(_LOCALES_DIR, filename)
        try:
            data = _load_locale_file(filepath)
            # 从 _meta.locale 获取语言代码，如果没有则用文件名
            locale_code = data.get("_meta", {}).get(
                "locale", filename.replace(".json", "")
            )
            locales[locale_code] = data
        except (json.JSONDecodeError, IOError) as e:
            st.warning(f"⚠️ Failed to load locale file {filename}: {e}")

    return locales


def get_available_locales() -> List[dict]:
    """
    获取所有可用语言的元信息列表
    返回: [{"locale": "en", "name": "English", "nativeName": "English"}, ...]
    """
    locales = _discover_locales()
    result = []
    for code, data in locales.items():
        meta = data.get("_meta", {})
        result.append({
            "locale": code,
            "name": meta.get("name", code),
            "nativeName": meta.get("nativeName", code),
            "direction": meta.get("direction", "ltr"),
        })
    return result


# ======================== 语言设置 ========================

def get_lang() -> str:
    """获取当前语言代码"""
    return st.session_state.get("locale", _FALLBACK_LOCALE)


def set_lang(locale_code: str):
    """设置当前语言"""
    st.session_state["locale"] = locale_code


# ======================== 核心翻译函数 ========================

def _resolve_key(data: dict, dotted_key: str) -> Optional[str]:
    """
    通过点分 key 从嵌套字典中取值
    例如: _resolve_key(data, "charts.axis.date") → data["charts"]["axis"]["date"]
    """
    try:
        return reduce(
            lambda d, k: d[k] if isinstance(d, dict) else None,
            dotted_key.split("."),
            data,
        )
    except (KeyError, TypeError):
        return None


def t(key: str, **kwargs) -> str:
    """
    核心翻译函数

    用法:
        t("app.title")                         → "📊 AI-Powered Sales Analytics"
        t("charts.top_products", n=10)         → "🏆 Top 10 Products by Sales"
        t("forecast.months", n=6)              → "6 months"
        t("ask_ai.samples.q1")                 → "Which region has the highest..."

    回退机制:
        当前语言 → 英文 → "[key]"
    """
    locales = _discover_locales()
    current_lang = get_lang()

    # 1. 尝试当前语言
    current_data = locales.get(current_lang, {})
    value = _resolve_key(current_data, key)

    # 2. 回退到英文
    if value is None and current_lang != _FALLBACK_LOCALE:
        fallback_data = locales.get(_FALLBACK_LOCALE, {})
        value = _resolve_key(fallback_data, key)

    # 3. 都找不到，返回 key 本身
    if value is None:
        return f"[{key}]"

    # 4. 如果取到的不是字符串（比如取到了一个子字典），返回 key
    if not isinstance(value, str):
        return f"[{key}]"

    # 5. 字符串插值
    if kwargs:
        try:
            value = value.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass

    return value


# ======================== 侧边栏语言切换器 ========================

def render_language_selector():
    """
    在侧边栏渲染语言切换下拉框
    自动从 locales/ 目录发现所有可用语言
    """
    available = get_available_locales()

    if not available:
        st.warning("No language packs found in locales/")
        return

    st.markdown(f"### {t('sidebar.language')}")

    current = get_lang()

    # 构建选项: 显示 nativeName (name) 格式
    options = []
    locale_codes = []
    current_idx = 0

    for i, loc in enumerate(available):
        native = loc["nativeName"]
        name = loc["name"]
        label = f"{native}" if native == name else f"{native} ({name})"
        options.append(label)
        locale_codes.append(loc["locale"])
        if loc["locale"] == current:
            current_idx = i

    selected = st.selectbox(
        "Language",
        options=options,
        index=current_idx,
        key="_locale_selector",
        label_visibility="collapsed",
    )

    new_locale = locale_codes[options.index(selected)]
    if new_locale != current:
        set_lang(new_locale)
        st.rerun()