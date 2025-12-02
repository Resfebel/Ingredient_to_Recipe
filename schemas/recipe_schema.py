from pydantic import BaseModel
from typing import List

# 입출력 구조
class Request(BaseModel):
    username: str
    ingredient: str

class Recipe(BaseModel):
    menu: str
    ingredient: str
    step: str

class Response(BaseModel):
    recipes: List[Recipe]