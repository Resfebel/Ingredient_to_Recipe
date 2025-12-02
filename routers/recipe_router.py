from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from google import genai

from schemas.recipe_schema import Recipe, Request
from services.gemini_service import recipes_by_gemini
from dependencies.user_dependency import get_current_user_name



# 동작 프롬프트가 1개니까 prefix 없이.
router = APIRouter()


# 사용자 반환
gemini_client = None
def get_client():
    if gemini_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Gemini Client가 초기화되지 않았습니다. API키를 확인하세요.")
    return gemini_client

@router.post("/recipes", status_code=status.HTTP_200_OK,
             summary="레시피 제공", response_model = Recipe)
async def create_recipe(request: Request, username: str = Depends(get_current_user_name),
                        client: genai.Client = Depends(get_client)):
    print(f"{username} request received for : {request.ingredient}")

    try:
        response_data = await recipes_by_gemini(client, request.ingredient)
        # 무조건 JSON 타입으로 반환해야 함

        return JSONResponse(content = response_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"router/service 층에서 오류가 발생했습니다: {e}"
        )
