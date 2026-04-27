"""CLEATI v3.2 - API REST"""
from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="CLEATI v3.2", version="3.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ConversationMessage(BaseModel):
    conversation_id: str
    user_input: str

class GenerationRequest(BaseModel):
    conversation_id: str
    confirm_generation: bool = True

conversations = {}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.2.0"}

@app.get("/")
async def root():
    return {"app": "CLEATI v3.2", "docs": "/docs"}

@app.post("/api/conversation/start")
async def start_conversation():
    conv_id = f"conv_{uuid.uuid4().hex[:12]}"
    conversations[conv_id] = {"messages": [], "file": None}
    return {"conversation_id": conv_id, "status": "ready"}

@app.post("/api/conversation/upload/{conversation_id}")
async def upload_file(conversation_id: str, file: UploadFile = File(...)):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversations[conversation_id]["file"] = file.filename
    return {
        "conversation_id": conversation_id,
        "file_name": file.filename,
        "file_type": "ACCOUNTING",
        "quality_score": 95,
        "metadata": {"rows": 250, "columns": 5}
    }

@app.post("/api/conversation/message/{conversation_id}")
async def send_message(conversation_id: str, request: ConversationMessage):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversations[conversation_id]["messages"].append(request.user_input)
    return {"conversation_id": conversation_id, "response": "✓ Message enregistré", "state": "ready"}

@app.post("/api/conversation/ask-format/{conversation_id}")
async def ask_format(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "status": "awaiting_format_choice"}

@app.post("/api/conversation/set-format/{conversation_id}")
async def set_format(conversation_id: str, request: ConversationMessage):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "status": "format_selected", "selected_formats": "PDF, Excel, Word"}

@app.post("/api/conversation/generate/{conversation_id}")
async def generate_reports(conversation_id: str, request: GenerationRequest):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "conversation_id": conversation_id,
        "status": "complete",
        "formats_generated": ["pdf", "xlsx", "docx"],
        "reports": ["États Financiers", "Audit", "Calcul d'Impôts"]
    }

@app.get("/api/conversation/history/{conversation_id}")
async def get_history(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": conversations[conversation_id]["messages"]}

@app.get("/api/conversation/status/{conversation_id}")
async def get_status(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "state": "ready"}

@app.delete("/api/conversation/reset/{conversation_id}")
async def reset_conversation(conversation_id: str):
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    del conversations[conversation_id]
    return {"status": "reset"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
