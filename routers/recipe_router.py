from fastapi import APIRouter, HTTPException, status, Depends, WebSocket
from fastapi.responses import JSONResponse
from google import genai
from starlette.websockets import WebSocketDisconnect

from schemas.recipe_schema import Recipe, Request
from services.gemini_service import streaming_recipes_by_gemini
from dependencies.user_dependency import get_current_user_name
from managers.connection_manager import manager


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


# 웹소켓을 연결하는 엔드포인트
@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str, client: genai.Client = Depends(get_client)):
    # 새로운 사용자 연결 등록
    await manager.connect(username, websocket)
    try:
        # 루프 유지되는 동안에는 계속해서 통신상태(연결) 유지
        while True:
            # -> 입력받은 메세지(재료)를 전달
            ingredient_data = await websocket.receive_text()
            print(f"[{username}] 식재료 : {ingredient_data}")

            # " 수신 받았고 처리중임! " 메세지 수신
            await manager.send_message(username, f"(치즈가 {ingredient_data} 요리를 생각하는 중입니다 . . .)")

            # 모델 호출, 처리
            await streaming_recipes_by_gemini(client, ingredient_data, username)

    except WebSocketDisconnect:
        # 연결 해제
        manager.disconnect(username)
        print(f"유저 {username}님이 채팅을 떠났습니다.")
    except Exception as e:
        # 오류 -> 연결 해제 + 메세지 통보
        print(f"오류가 발생했습니다 for {username}: {e}")
        await manager.send_message(username, f"서버 오류: {e} - 연결이 종료됩니다")
        manager.disconnect(username)

"""
# 레시피 제공 엔드포인트
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
"""