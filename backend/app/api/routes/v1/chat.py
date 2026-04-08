"""
Chat Routes with Full Conversation Memory + Two‑Stage AI + IP‑Based Session
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import requests
from datetime import datetime
from collections import deque

from app.config import config
from app.api.dependencies.auth import get_current_user
from app.document_processor.vector_store import vector_store
from app.services.search_service import search_service
from app.utils.logger import logger

router = APIRouter()

# In-memory conversation history (stores messages per conversation_id)
conversation_memory = {}

# Simple IP‑based session mapping (for testing only)
ip_conversation_map = {}


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None
    use_web_search: bool = True
    research_mode: bool = False
    temperature: float = 0.7
    max_tokens: int = config.MAX_TOKENS_PER_QUERY


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: List[Dict] = []
    cost: float = 0.0
    tokens_used: int = 0
    processing_time: float = 0.0
    document_used: bool = False
    direct_answer: Optional[str] = None


async def get_conversation_history(conversation_id: str, limit: int = 50) -> List[Dict]:
    """Get conversation history"""
    if conversation_id not in conversation_memory:
        conversation_memory[conversation_id] = deque(maxlen=config.MAX_CONVERSATION_MESSAGES)
    return list(conversation_memory[conversation_id])[-limit:]


async def save_to_conversation(conversation_id: str, role: str, content: str, metadata: Dict = None):
    """Save message to conversation memory"""
    if conversation_id not in conversation_memory:
        conversation_memory[conversation_id] = deque(maxlen=config.MAX_CONVERSATION_MESSAGES)
    conversation_memory[conversation_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    })


async def call_deepseek(prompt: str, temperature: float, max_tokens: int, api_key: str) -> Dict[str, Any]:
    """Helper to call DeepSeek API with timeout and retry"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)  # increased timeout
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            tokens = len(content) // 4
            return {"content": content, "tokens": tokens}
        else:
            logger.error(f"DeepSeek API error: {response.status_code}")
            return {"content": "", "tokens": 0}
    except Exception as e:
        logger.error(f"DeepSeek call failed: {e}")
        return {"content": "", "tokens": 0}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    http_request: Request,  # for client IP
    current_user: dict = Depends(get_current_user)
):
    """
    Chat with automatic conversation memory based on client IP (session).
    """
    # ========================================================================
    # Determine conversation_id: explicit ID > IP session > new ID
    # ========================================================================
    if request.conversation_id:
        conversation_id = request.conversation_id
        print(f"📌 Using explicit conversation_id: {conversation_id[:8]}...")
    else:
        # Build session key from IP and User-Agent (simple but works for testing)
        client_ip = http_request.client.host if http_request.client else "unknown"
        user_agent = http_request.headers.get("User-Agent", "unknown")[:50]
        session_key = f"{client_ip}:{user_agent}"
        
        if session_key in ip_conversation_map:
            conversation_id = ip_conversation_map[session_key]
            print(f"♻️ Reusing conversation_id {conversation_id[:8]}... for {session_key[:50]}")
        else:
            conversation_id = str(uuid.uuid4())
            ip_conversation_map[session_key] = conversation_id
            print(f"🆕 Created new conversation_id {conversation_id[:8]}... for {session_key[:50]}")

    start_time = datetime.utcnow()

    api_key = config.DEEPSEEK_API_KEY.strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="DeepSeek API key not configured")

    print(f"\n{'='*60}")
    print(f"📝 Question: {request.message}")
    print(f"📄 Document ID: {request.document_id or 'None'}")
    print(f"🌐 Web Search: {request.use_web_search}")
    print(f"🆔 Conversation ID: {conversation_id[:8]}...")
    print(f"{'='*60}")

    # ========================================================================
    # LOAD CONVERSATION HISTORY
    # ========================================================================
    history = await get_conversation_history(conversation_id, limit=20)
    history_text = ""
    if history:
        history_text = "\n\n## Previous conversation:\n"
        for msg in history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content'][:500]}\n"
        print(f"💾 Loaded {len(history)} previous messages")

    direct_answer = ""
    sources = []
    contexts = []
    document_used = False

    # ========================================================================
    # STAGE 1: Direct answer with conversation history
    # ========================================================================
    if request.use_web_search or request.research_mode:
        direct_prompt = f"""{history_text}

Current question: {request.message}

Answer concisely based on your knowledge and the conversation history. Keep it under 150 words."""
        direct_result = await call_deepseek(direct_prompt, request.temperature, 500, api_key)
        direct_answer = direct_result["content"]
        print(f"\n📝 Direct answer: {direct_answer[:100]}...")

    # ========================================================================
    # STAGE 2: Search web and/or documents
    # ========================================================================
    if request.use_web_search or request.research_mode:
        print(f"\n🌐 Searching web...")
        try:
            search_results = await search_service.search_all(request.message, 3)
            for result in search_results[:10]:
                contexts.append({
                    'content': result.get('content', result.get('summary', ''))[:1500],
                    'source': result.get('engine', 'Web'),
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'relevance': result.get('relevance', 0.5)
                })
                sources.append({
                    "type": "search",
                    "engine": result.get('engine', 'Web'),
                    "title": result.get('title', ''),
                    "url": result.get('url', ''),
                    "relevance": result.get('relevance', 0.5)
                })
            print(f"✅ Found {len(search_results)} web results")
        except Exception as e:
            print(f"⚠️ Web search error: {e}")

    if request.document_id:
        try:
            print(f"\n📖 Searching document {request.document_id[:8]}...")
            chunks = await vector_store.search_document(
                document_id=request.document_id,
                query=request.message,
                k=config.MAX_RETRIEVED_CHUNKS
            )
            if chunks:
                document_used = True
                print(f"✅ Found {len(chunks)} document chunks")
                for chunk in chunks[:5]:
                    contexts.append({
                        'content': chunk['text'][:1500],
                        'source': 'document',
                        'title': chunk['metadata'].get('filename', 'Document'),
                        'relevance': chunk['score']
                    })
                    sources.append({
                        "type": "document",
                        "title": chunk['metadata'].get('filename', 'Document'),
                        "relevance": chunk['score']
                    })
        except Exception as e:
            print(f"❌ Document error: {e}")

    # ========================================================================
    # STAGE 3: Refine answer using search results and conversation history
    # ========================================================================
    final_answer = direct_answer
    if contexts and (request.use_web_search or document_used):
        context_text = "\n\n".join([
            f"[Source {i}]: {ctx['content']}" 
            for i, ctx in enumerate(contexts[:10], 1)
        ])

        synthesis_prompt = f"""{history_text}

INITIAL ANSWER (based on your knowledge):
{direct_answer if direct_answer else "(No initial answer)"}

ADDITIONAL SOURCES (web search and/or documents):
{context_text}

ORIGINAL QUESTION: {request.message}

Please produce a FINAL, IMPROVED answer that:
- Incorporates relevant facts from the additional sources.
- Corrects any errors in the initial answer.
- Is clear, concise, and well‑structured.
- If the additional sources contradict your initial answer, favour the sources.

FINAL ANSWER:
"""
        refined = await call_deepseek(synthesis_prompt, request.temperature, request.max_tokens, api_key)
        if refined["content"]:
            final_answer = refined["content"]
            print(f"\n✨ Refined answer generated using {len(contexts)} sources")
        else:
            print("⚠️ Refinement failed, using direct answer")

    # ========================================================================
    # SAVE TO CONVERSATION MEMORY
    # ========================================================================
    await save_to_conversation(conversation_id, "user", request.message)
    await save_to_conversation(conversation_id, "assistant", final_answer, {"sources": sources})

    processing_time = (datetime.utcnow() - start_time).total_seconds()
    tokens_used = len(final_answer) // 4
    cost = (tokens_used / 1_000_000) * 0.28

    print(f"\n✅ Final answer length: {len(final_answer)} chars, {tokens_used} tokens, {processing_time:.2f}s")
    print(f"{'='*60}\n")

    return ChatResponse(
        answer=final_answer,
        conversation_id=conversation_id,
        sources=sources,
        cost=cost,
        tokens_used=tokens_used,
        processing_time=processing_time,
        document_used=document_used,
        direct_answer=direct_answer if direct_answer else None
    )