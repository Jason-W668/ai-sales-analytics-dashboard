"""
配置管理模块
"""

import os
import yaml
import streamlit as st
from dataclasses import dataclass
from typing import Optional
from modules.i18n import t


@dataclass
class ProviderConfig:
    name: str
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    display_name: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(
            self.api_key and self.api_key.strip()
            and self.api_key != "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )


PROVIDERS = {
    "siliconflow": {
        "display_name": "🌊 硅基流动 (SiliconFlow)",
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Pro/deepseek-ai/DeepSeek-V3.2",
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
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "help_url": "https://platform.openai.com/api-keys",
        "key_prefix": "sk-",
    },
}


def _find_config_file() -> Optional[str]:
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
    config_path = _find_config_file()
    if not config_path:
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config if isinstance(config, dict) else {}
    except Exception as e:
        st.warning(f"⚠️ config.yaml: {e}")
        return {}


def get_local_provider_config(provider_name: str) -> ProviderConfig:
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
    return load_local_config().get("default_provider", "siliconflow")


def get_active_config() -> Optional[ProviderConfig]:
    provider_name = st.session_state.get("selected_provider", get_default_provider())
    frontend_key = st.session_state.get("frontend_api_key", "").strip()
    selected_model = st.session_state.get("selected_model", "")

    config = get_local_provider_config(provider_name)
    provider_info = PROVIDERS.get(provider_name, {})

    if frontend_key:
        config.api_key = frontend_key
    if selected_model:
        config.model = selected_model
    if not config.base_url:
        config.base_url = provider_info.get("base_url", "")
    if not config.model:
        config.model = provider_info.get("default_model", "")
    return config


def render_ai_sidebar():
    """渲染 AI 配置侧边栏"""
    st.markdown(f"### {t('sidebar.ai.configuration')}")

    default_provider = get_default_provider()
    provider_names = list(PROVIDERS.keys())
    provider_labels = [PROVIDERS[p]["display_name"] for p in provider_names]
    default_idx = provider_names.index(default_provider) if default_provider in provider_names else 0

    selected_label = st.selectbox(
        t("sidebar.ai.provider"), options=provider_labels,
        index=default_idx, key="_provider_select",
    )
    selected_provider = provider_names[provider_labels.index(selected_label)]
    st.session_state["selected_provider"] = selected_provider

    provider_info = PROVIDERS[selected_provider]
    local_provider = get_local_provider_config(selected_provider)

    models = provider_info["models"]
    default_model = local_provider.model or provider_info["default_model"]
    default_model_idx = models.index(default_model) if default_model in models else 0

    selected_model = st.selectbox(
        t("sidebar.ai.model"), options=models,
        index=default_model_idx, key="_model_select",
    )
    st.session_state["selected_model"] = selected_model

    if local_provider.is_configured:
        masked = local_provider.api_key[:6] + "****" + local_provider.api_key[-4:]
        st.success(f"🔑 {t('sidebar.ai.local_key_found')}: `{masked}`")
        st.caption(t("sidebar.ai.using_local_key"))
    else:
        st.info(t("sidebar.ai.no_local_key"))

    st.markdown(
        f'<p style="font-size:12px;color:#999;margin-bottom:2px;">'
        f'{t("sidebar.ai.enter_key_hint")}</p>',
        unsafe_allow_html=True,
    )

    frontend_key = st.text_input(
        "API Key", type="password",
        placeholder=t("sidebar.ai.key_placeholder"),
        key="_frontend_key_input", label_visibility="collapsed",
    )
    st.session_state["frontend_api_key"] = frontend_key

    active_config = get_active_config()

    if active_config and active_config.is_configured:
        source = t("sidebar.ai.frontend_input") if frontend_key.strip() else "config.yaml"
        st.markdown(
            f"""<div style="background:rgba(76,175,80,0.1);border-left:3px solid #4CAF50;
            padding:8px 12px;border-radius:0 6px 6px 0;margin-top:8px;">
            <span style="color:#81C784;font-size:13px;">
            {t('sidebar.ai.ready')} | {t('sidebar.ai.source')}: {source}<br>
            📡 {active_config.display_name}<br>
            🧠 {active_config.model}</span></div>""",
            unsafe_allow_html=True,
        )
    else:
        help_url = provider_info["help_url"]
        st.markdown(
            f"""<div style="background:rgba(255,152,0,0.1);border-left:3px solid #FF9800;
            padding:8px 12px;border-radius:0 6px 6px 0;margin-top:8px;">
            <span style="color:#FFB74D;font-size:13px;">
            {t('sidebar.ai.no_key_configured')}<br>
            <a href="{help_url}" target="_blank" style="color:#4FC3F7;">
            {t('sidebar.ai.get_key_here')}</a></span></div>""",
            unsafe_allow_html=True,
        )

    return active_config