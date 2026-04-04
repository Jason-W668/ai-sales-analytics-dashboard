"""
配置管理模块
支持从本地 config.yaml 读取配置，也支持前端动态输入
前端输入的 API Key 仅存在于 session 中，不会持久化
"""

import os
import yaml
import streamlit as st
from dataclasses import dataclass, field
from typing import Optional


# ======================== 数据结构 ========================

@dataclass
class ProviderConfig:
    """单个 AI 服务商的配置"""
    name: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    display_name: str = ""

    @property
    def is_configured(self) -> bool:
        """是否已配置 API Key"""
        return bool(self.api_key and self.api_key.strip()
                     and self.api_key != "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


# ======================== 预定义服务商 ========================

PROVIDERS = {
    "siliconflow": {
        "display_name": "🌊 硅基流动 (SiliconFlow)",
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-72B-Instruct",
        "models": [
            "Pro/deepseek-ai/DeepSeek-V3.2",
            "Pro/moonshotai/Kimi-K2.5",
            "Pro/MiniMaxAI/MiniMax-M2.5",
            "Qwen/Qwen2.5-72B-Instruct",
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-32B-Instruct",
            "Pro/Qwen/Qwen2.5-7B-Instruct",
            "THUDM/glm-4-9b-chat",
        ],
        "help_url": "https://cloud.siliconflow.cn/account/ak",
        "key_prefix": "sk-",
    },
    "openai": {
        "display_name": "🤖 OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "help_url": "https://platform.openai.com/api-keys",
        "key_prefix": "sk-",
    },
}


# ======================== 加载本地配置 ========================

def _find_config_file() -> Optional[str]:
    """查找 config.yaml 文件"""
    candidates = [
        os.path.join(os.getcwd(), "config.yaml"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


@st.cache_data
def load_local_config() -> dict:
    """
    从 config.yaml 加载本地配置
    缓存结果，只在启动时读取一次
    """
    config_path = _find_config_file()
    if not config_path:
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config if isinstance(config, dict) else {}
    except Exception as e:
        st.warning(f"⚠️ Failed to read config.yaml: {e}")
        return {}


def get_local_provider_config(provider_name: str) -> ProviderConfig:
    """从本地配置获取指定服务商的配置"""
    config = load_local_config()
    provider_info = PROVIDERS.get(provider_name, {})

    provider_conf = config.get(provider_name, {})

    return ProviderConfig(
        name=provider_name,
        api_key=provider_conf.get("api_key", ""),
        base_url=provider_conf.get("base_url", provider_info.get("base_url", "")),
        model=provider_conf.get("model", provider_info.get("default_model", "")),
        display_name=provider_info.get("display_name", provider_name),
    )


def get_default_provider() -> str:
    """获取默认服务商名称"""
    config = load_local_config()
    return config.get("default_provider", "siliconflow")


# ======================== 运行时配置（合并本地+前端） ========================

def get_active_config() -> Optional[ProviderConfig]:
    """
    获取当前生效的 AI 配置
    优先级: 前端输入 > 本地配置文件
    前端输入仅保存在 st.session_state 中，刷新页面后消失
    """

    # 从 session_state 读取当前选择
    provider_name = st.session_state.get("selected_provider", get_default_provider())
    frontend_key = st.session_state.get("frontend_api_key", "").strip()
    selected_model = st.session_state.get("selected_model", "")

    # 先取本地配置作为基础
    config = get_local_provider_config(provider_name)
    provider_info = PROVIDERS.get(provider_name, {})

    # 前端输入的 Key 优先（覆盖本地配置，但不保存到文件）
    if frontend_key:
        config.api_key = frontend_key

    # 前端选择的模型优先
    if selected_model:
        config.model = selected_model

    # 确保 base_url 有值
    if not config.base_url:
        config.base_url = provider_info.get("base_url", "")

    # 确保 model 有值
    if not config.model:
        config.model = provider_info.get("default_model", "")

    return config


# ======================== 侧边栏 UI 组件 ========================

def render_ai_sidebar():
    """
    渲染侧边栏的 AI 配置区域
    返回当前生效的配置
    """

    st.markdown("### 🤖 AI Configuration")

    local_config = load_local_config()
    default_provider = get_default_provider()

    # ---- 服务商选择 ----
    provider_names = list(PROVIDERS.keys())
    provider_labels = [PROVIDERS[p]["display_name"] for p in provider_names]

    default_idx = (
        provider_names.index(default_provider)
        if default_provider in provider_names
        else 0
    )

    selected_label = st.selectbox(
        "AI Provider",
        options=provider_labels,
        index=default_idx,
        key="_provider_select",
    )
    selected_provider = provider_names[provider_labels.index(selected_label)]
    st.session_state["selected_provider"] = selected_provider

    provider_info = PROVIDERS[selected_provider]
    local_provider = get_local_provider_config(selected_provider)

    # ---- 模型选择 ----
    models = provider_info["models"]
    default_model = local_provider.model or provider_info["default_model"]
    default_model_idx = models.index(default_model) if default_model in models else 0

    selected_model = st.selectbox(
        "Model",
        options=models,
        index=default_model_idx,
        key="_model_select",
    )
    st.session_state["selected_model"] = selected_model

    # ---- API Key 状态显示 ----
    has_local_key = local_provider.is_configured

    if has_local_key:
        masked = local_provider.api_key[:6] + "****" + local_provider.api_key[-4:]
        st.success(f"🔑 Local Key: `{masked}`")
        st.caption("✅ Using API Key from config.yaml")
    else:
        st.info("💡 No local key found in config.yaml")

    # ---- 前端 Key 输入（不保存） ----
    st.markdown(
        '<p style="font-size:12px; color:#999; margin-bottom:2px;">'
        "Enter API Key below to override (not saved):</p>",
        unsafe_allow_html=True,
    )

    frontend_key = st.text_input(
        "API Key (temporary)",
        type="password",
        placeholder=f"Enter {provider_info['display_name']} API Key...",
        key="_frontend_key_input",
        label_visibility="collapsed",
    )

    # 存入 session_state 但不写入文件
    st.session_state["frontend_api_key"] = frontend_key

    # ---- 状态指示 ----
    active_config = get_active_config()

    if active_config and active_config.is_configured:
        source = "Frontend Input" if frontend_key.strip() else "config.yaml"
        st.markdown(
            f"""<div style="background: rgba(76,175,80,0.1); border-left: 3px solid #4CAF50;
            padding: 8px 12px; border-radius: 0 6px 6px 0; margin-top: 8px;">
            <span style="color: #81C784; font-size: 13px;">
            ✅ Ready &nbsp;|&nbsp; Source: {source}<br>
            📡 {active_config.display_name}<br>
            🧠 {active_config.model}
            </span></div>""",
            unsafe_allow_html=True,
        )
    else:
        help_url = provider_info["help_url"]
        st.markdown(
            f"""<div style="background: rgba(255,152,0,0.1); border-left: 3px solid #FF9800;
            padding: 8px 12px; border-radius: 0 6px 6px 0; margin-top: 8px;">
            <span style="color: #FFB74D; font-size: 13px;">
            ⚠️ No API Key configured<br>
            <a href="{help_url}" target="_blank" style="color: #4FC3F7;">
            Get your key here →</a>
            </span></div>""",
            unsafe_allow_html=True,
        )

    return active_config