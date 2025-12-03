from google import genai
from google.genai.errors import APIError

from schemas.recipe_schema import RecipesResponse
from managers.connection_manager import manager

import json
import asyncio

# GEMINI 다루는 서비스로직

SYSTEM_PROMPT = """
너는 주어진 식재료로 만들 수 있는 레시피를 3가지 추천해주는 요리 전문 AI 챗봇이야.
사용자가 정해주는 식재료를 주재료로 하는 레시피를 제안해야 해.
레시피는 너무 자세하게 말고 간략하게 3-4줄 정도로 정리해서 제공해야 해.
앞에 인사는 생략하고, 존댓말로 답변해.
레시피 메뉴 이름에 bold체는 빼고, 메뉴 이름 뒤에 어울리는 이모티콘 하나를 붙여.
"""


# 레시피 생성 함수 (웹소켓-스트리밍 처리)
async def streaming_recipes_by_gemini(client: genai.Client, ingredient: str, username: str):
    user_prompt = f"다음 식재료를 사용해 레시피를 3개 추천해줘. 식재료 : {ingredient}"

    try:
        # streaming 호출
        response_stream = client.models.generate_content_stream(
            model = "gemini-2.5-flash",
            contents = [SYSTEM_PROMPT, user_prompt]
            # streaming 시에는 답변을 JSON이 아닌 일반 텍스트로 받기 때문에 config는 패스~!
        )

        await manager.send_message(username, "--- 레시피 ---")

        def stream_generator():
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        for text_chunk in await asyncio.to_thread(stream_generator):
            await manager.send_message(username, text_chunk)

        await manager.send_message(username, "--- 레시피 생성 완료 ---")

    except APIError as e:
        await manager.send_message(username, f"API 오류가 발생했습니다: {e}")
        raise
    except Exception as e:
        await manager.send_message(username, f"레시피 생성 중 오류가 발생했습니다: {e}")
        raise


# 레시피 생성 함수 (old)
"""
async def recipes_by_gemini(client: genai.Client, ingredient: str) -> dict:
    user_prompt = f"다음 식재료를 사용해 레시피를 3개 추천해줘. 식재료 : {ingredient}"

    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [SYSTEM_PROMPT, user_prompt],
            config = genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema = RecipesResponse
            )
        )

        json_string = response.text.strip()
        recipe_data = json.loads(json_string)
        return recipe_data
    except APIError as e:
        raise Exception(f"모델 API 호출 중 오류가 발생했습니다: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"답변 -> JSON 파싱을 실패했습니다: {e}")
    except Exception as e:
        raise Exception(f"레시피 생성 중 오류가 발생했습니다: {e}")
"""