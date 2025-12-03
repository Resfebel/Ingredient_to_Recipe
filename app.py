from dotenv import load_dotenv
from fastapi import FastAPI, Request
from google import genai
import uvicorn
from starlette.templating import Jinja2Templates

from routers import recipe_router

# 환경 변수 모셔오기
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# gemini 초기화
try:
    client = genai.Client()
    print("Gemini Client initialized successfully")
    # router의 client에 현재 사용자(client) 주입
    recipe_router.gemini_client = client
except Exception as e:
    print(f"Gemini 초기화 실패 : {e}")

# 라우터 연결
app.include_router(recipe_router.router)


# HTML
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        #name = "index.html",
        name="index_chatbot.html",
        context = {"request": request},
    )

if __name__ == "__main__":
    uvicorn.run(app, reload = True)