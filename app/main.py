import json
import os
from pathlib import Path
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FAQ_PATH = BASE_DIR / "data" / "faq.json"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="E-commerce AI Assistant",
    description="一个适合新手开源的电商运营 AI 客服助手，支持离线 FAQ 匹配和可选大模型 API。",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: List[ChatMessage] = Field(default_factory=list)
    use_ai: bool = True


class ChatResponse(BaseModel):
    reply: str
    source: str
    matched_faq: Optional[str] = None


def load_faqs():
    with FAQ_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


FAQS = load_faqs()


def score_faq(message: str, faq: dict) -> int:
    text = message.lower().strip()
    score = 0
    for keyword in faq.get("keywords", []):
        if keyword.lower() in text:
            score += 3 if len(keyword) >= 3 else 1
    if faq.get("question") and faq["question"].lower() in text:
        score += 5
    return score


def find_faq(message: str):
    best = None
    best_score = 0
    for faq in FAQS:
        score = score_faq(message, faq)
        if score > best_score:
            best = faq
            best_score = score
    return best if best_score >= 2 else None


def build_faq_context() -> str:
    return "\n".join(
        f"问题：{item['question']}\n回答：{item['answer']}"
        for item in FAQS
    )


async def call_llm(message: str, history: List[ChatMessage], faq_answer: Optional[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        return faq_answer or "我暂时没有完全理解这个问题。您可以描述订单号、商品问题或上传售后凭证，也可以回复“人工客服”转接专员。"

    system_prompt = (
        "你是电商店铺的售后客服，语气礼貌、简洁、可靠。"
        "只能依据知识库回答；知识库没有明确信息时，不要编造承诺，"
        "应提示用户联系人工客服或查看订单售后页。\n\n"
        f"知识库：\n{build_faq_context()}"
    )
    if faq_answer:
        system_prompt += f"\n\n最相关的标准答复：{faq_answer}"

    messages = [{"role": "system", "content": system_prompt}]
    for item in history[-6:]:
        messages.append({"role": item.role, "content": item.content})
    messages.append({"role": "user", "content": message})

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": model, "messages": messages, "temperature": 0.3},
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return faq_answer or "当前 AI 服务暂时不可用，已为您切换到标准知识库答复。您也可以回复“人工客服”。"


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/faqs")
def get_faqs():
    return FAQS


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    matched = find_faq(request.message)
    faq_answer = matched["answer"] if matched else None

    if request.use_ai:
        reply = await call_llm(request.message, request.history, faq_answer)
        source = "llm_with_faq" if os.getenv("OPENAI_API_KEY", "").strip() else "faq_fallback"
    else:
        reply = faq_answer or "抱歉，我还没有匹配到这个问题。您可以换个说法，或回复“人工客服”联系售后专员。"
        source = "faq"

    return ChatResponse(
        reply=reply,
        source=source,
        matched_faq=matched["id"] if matched else None,
    )
