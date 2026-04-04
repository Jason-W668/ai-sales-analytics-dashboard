"""
AI 智能分析模块 - 从语言包读取 prompt
"""

from openai import OpenAI
from modules.i18n import t


def _create_client(api_key: str, base_url: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url)


def generate_insights(data_summary: str, api_key: str,
                       base_url: str = "https://api.openai.com/v1",
                       model: str = "gpt-4o") -> str:
    try:
        client = _create_client(api_key, base_url)

        system_prompt = t("ai_prompts.insight_system")
        lang_instruction = t("ai_prompts.language_instruction")
        full_prompt = f"{system_prompt}\n\n{lang_instruction}"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": f"Please analyze this sales data and provide your expert insights:\n\n{data_summary}"},
            ],
            temperature=0.7,
            max_tokens=2500,
        )
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return "❌ **Authentication Failed**: Invalid API Key."
        elif "429" in error_msg:
            return "❌ **Rate Limited**: Please wait and try again."
        elif "insufficient_quota" in error_msg or "402" in error_msg:
            return "❌ **Insufficient Quota**: Please top up your account."
        elif "model" in error_msg.lower() and "not found" in error_msg.lower():
            return f"❌ **Model Not Found**: `{model}` is not available."
        else:
            return f"❌ **Error**: {error_msg}"


def answer_question(question: str, data_summary: str, api_key: str,
                     base_url: str = "https://api.openai.com/v1",
                     model: str = "gpt-4o") -> str:
    try:
        client = _create_client(api_key, base_url)

        qa_prompt = t("ai_prompts.qa_system")
        lang_instruction = t("ai_prompts.language_instruction")

        system_content = f"{qa_prompt}\n\nHere is the complete data summary:\n\n{data_summary}\n\n{lang_instruction}"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": question},
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return "❌ **Authentication Failed**: Invalid API Key."
        elif "429" in error_msg:
            return "❌ **Rate Limited**: Please wait and try again."
        elif "model" in error_msg.lower() and "not found" in error_msg.lower():
            return f"❌ **Model Not Found**: `{model}` is not available."
        else:
            return f"❌ **Error**: {error_msg}"