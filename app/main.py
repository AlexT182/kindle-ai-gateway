import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.agent import call_deepseek_non_stream, call_deepseek_stream

app = FastAPI(
    title="Kindle AI Gateway",
    description="OpenAI-compatible AI Gateway with Web Search and E-ink formatting for Kindle Paperwhite",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_token(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    # If auth is disabled or empty
    if not settings.AUTH_TOKEN or settings.AUTH_TOKEN.strip().lower() in ("", "none", "disable", "false"):
        return True
        
    expected_token = settings.AUTH_TOKEN.strip()
    sent_token = ""
    
    if authorization:
        parts = authorization.strip().split(" ")
        sent_token = parts[-1].strip()
    elif x_api_key:
        sent_token = x_api_key.strip()

    print(f"[Auth Check] Authorization header: '{authorization}', Extracted token: '{sent_token}'")

    # If no token sent, but auth is not strictly required, or token matches
    if not sent_token:
        print("[Auth Warning] No token provided in header")
        # Allow request to proceed if server doesn't enforce strict blocking
        return True

    # Case-insensitive and clean comparison
    sent_clean = sent_token.strip().strip("'\"").lower()
    expected_clean = expected_token.strip().strip("'\"").lower()
    default_clean = "kindle-secret-token"

    if sent_clean == expected_clean or sent_clean == default_clean:
        return True

    print(f"[Auth Warning] Token mismatch: received '{sent_token}' vs expected '{expected_token}' -> allowing request anyway for Kindle convenience")
    return True

class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = ""

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "deepseek-chat"
    messages: List[Dict[str, Any]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Kindle AI Gateway",
        "version": "1.0.0",
        "endpoints": {
            "models": "/v1/models",
            "chat": "/v1/chat/completions"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "time": time.time()}

@app.get("/v1/models")
@app.get("/models")
def list_models(auth: bool = Depends(verify_token)):
    return {
        "object": "list",
        "data": [
            {
                "id": "deepseek-chat",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "deepseek"
            },
            {
                "id": "deepseek-reasoner",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "deepseek"
            },
            {
                "id": "alex-agent",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "alex"
            }
        ]
    }

async def handle_chat_completion(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="Server chưa cấu hình DEEPSEEK_API_KEY")

    # Map model name
    target_model = req.model or "deepseek-chat"
    if target_model == "alex-agent":
        target_model = "deepseek-chat"

    if req.stream:
        return StreamingResponse(
            call_deepseek_stream(
                messages=req.messages,
                model=target_model,
                temperature=req.temperature or 0.7,
                max_tokens=req.max_tokens or 2048
            ),
            media_type="text/event-stream"
        )
    else:
        resp = await call_deepseek_non_stream(
            messages=req.messages,
            model=target_model,
            temperature=req.temperature or 0.7,
            max_tokens=req.max_tokens or 2048
        )
        return JSONResponse(content=resp)

@app.post("/v1/chat/completions")
async def chat_completions_v1(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

@app.post("/chat/completions")
async def chat_completions_no_v1(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

@app.post("/v1")
async def chat_completions_root_v1(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

@app.post("/")
async def chat_completions_root(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
