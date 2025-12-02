from schemas.recipe_schema import Request
from fastapi import Depends, HTTPException, status


def get_current_user_name(request: Request) -> str:
    username = request.username

    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail = {"사용자를 찾을 수 없습니다."})
    return username