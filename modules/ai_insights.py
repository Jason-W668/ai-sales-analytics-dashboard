"""
AI 智能分析模块
支持 OpenAI / 硅基流动(SiliconFlow) 等 OpenAI 兼容接口
"""

from openai import OpenAI
import streamlit as st


def _create_client(api_key: str, base_url: str) -> OpenAI:
    """创建 OpenAI 兼容客户端"""
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def generate_insights(data_summary: str, api_key: str,
                       base_url: str = "https://api.openai.com/v1",
                       model: str = "gpt-4o") -> str:
    """
    调用 AI 生成全面的商业分析洞察
    支持任何 OpenAI 兼容 API（OpenAI / 硅基流动 / 其他）
    """
    try:
        client = _create_client(api_key, base_url)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a senior business intelligence analyst with 15 years of retail analytics experience.

Analyze the provided Superstore sales data and deliver a comprehensive executive report.

FORMAT your response clearly with these sections (use markdown):

## 📊 Executive Summary
(2-3 sentence overview of the business performance)

## 🔍 Top 5 Key Findings
(Numbered list with specific numbers, percentages, and comparisons)

## ⚠️ Areas of Concern
(Identify 3-4 problem areas with data evidence - losses, declining trends, etc.)

## 💡 Strategic Recommendations
(5 actionable, specific recommendations based on the data)

## 📈 Growth Opportunities
(3 specific growth opportunities with estimated impact)

## 🎯 Quick Wins
(3 things that can be implemented immediately)

Be SPECIFIC with numbers. Compare regions, categories, segments.
Identify patterns, anomalies, and correlations.
Make recommendations data-driven and actionable.
Respond in English.""",
                },
                {
                    "role": "user",
                    "content": f"Please analyze this sales data and provide your expert insights:\n\n{data_summary}",
                },
            ],
            temperature=0.7,
            max_tokens=2500,
        )

        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e)

        # 友好错误提示
        if "401" in error_msg or "Unauthorized" in error_msg:
            return "❌ **Authentication Failed**: Invalid API Key. Please check your key and try again."
        elif "429" in error_msg:
            return "❌ **Rate Limited**: Too many requests. Please wait a moment and try again."
        elif "insufficient_quota" in error_msg or "402" in error_msg:
            return "❌ **Insufficient Quota**: Your API account has no remaining credits. Please top up."
        elif "model" in error_msg.lower() and "not found" in error_msg.lower():
            return f"❌ **Model Not Found**: The model `{model}` is not available. Please select a different model in the sidebar."
        else:
            return f"❌ **Error generating insights**: {error_msg}\n\nPlease check your API configuration and try again."


def answer_question(question: str, data_summary: str, api_key: str,
                     base_url: str = "https://api.openai.com/v1",
                     model: str = "gpt-4o") -> str:
    """
    回答用户关于数据的自然语言问题
    支持任何 OpenAI 兼容 API
    """
    try:
        client = _create_client(api_key, base_url)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful data analyst assistant. You have access to a Superstore retail sales dataset.

Here is the complete data summary:

{data_summary}

INSTRUCTIONS:
- Answer questions based ONLY on the data provided above
- Be specific with numbers, percentages, and comparisons
- If you cannot determine something from the data, say so clearly
- Format your answer with markdown for readability
- Use bullet points for lists
- Include relevant numbers to support your answer
- If the question involves a comparison, present it in a clear format
- Keep answers concise but thorough
- Respond in the same language as the user's question""",
                },
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
            return "❌ **Rate Limited**: Please wait a moment and try again."
        elif "model" in error_msg.lower() and "not found" in error_msg.lower():
            return f"❌ **Model Not Found**: `{model}` is not available. Please change the model."
        else:
            return f"❌ **Error**: {error_msg}"