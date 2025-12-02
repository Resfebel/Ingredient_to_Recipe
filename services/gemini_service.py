from google import genai
from google.genai.errors import APIError

from schemas.recipe_schema import Recipe, Response

import json

# GEMINI 다루는 서비스로직

SYSTEM_PROMPT = """
너는 주어진 식재료로 만들 수 있는 레시피를 3가지 추천해주는 요리 전문 AI 챗봇이야.
사용자가 정해주는 식재료를 주재료로 하는 레시피를 제안해야 해.
답변은 지정된 스키마 구조에 따라 JSON 형식으로 제공되어야 해.
레시피는 너무 자세하게 말고 간략하게 3-4줄 정도로 정리해서 제공해야 해.
존댓말로 답변해야 해.
"""

async def recipes_by_gemini(client: genai.Client, ingredient: str) -> dict:
    user_prompt = f"다음 식재료를 사용해 레시피를 3~5개 추천해줘. 식재료 : {ingredient}"

    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = [SYSTEM_PROMPT, user_prompt],
            config = genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema = Response
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