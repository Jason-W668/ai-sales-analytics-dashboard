"""
AI 智能分析模块
调用 OpenAI API 生成商业洞察和回答自然语言问题
"""

from openai import OpenAI
import streamlit as st


def generate_insights(data_summary: str, api_key: str) -> str:
    """
    调用 GPT 生成全面的商业分析洞察
    """
    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
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
Make recommendations data-driven and actionable.""",
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
        return f"❌ Error generating insights: {str(e)}\n\nPlease check your API key and try again."


def answer_question(question: str, data_summary: str, api_key: str) -> str:
    """
    回答用户关于数据的自然语言问题
    """
    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4o",
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
- Keep answers concise but thorough""",
                },
                {"role": "user", "content": question},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error: {str(e)}"