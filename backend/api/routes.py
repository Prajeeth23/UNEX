import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.agent.agent_manager import UNEXAgent
from src.voice.voice_controller import VoiceController
from src.memory.memory_models import MemoryType
from src.security.audit_logger import AuditLogger
from src.tools.application_catalog import ApplicationCatalog
from src.security.permissions import RiskLevel
from src.education.education_manager import EducationManager
from src.education.paper_analyzer import PaperAnalyzer
from src.vision.vision_manager import VisionManager
from src.rag.rag_manager import RAGManager
from src.automation.workflow_engine import WorkflowEngine
from src.monitoring.metrics import SystemMetrics
from src.monitoring.diagnostics import DiagnosticsEngine
from src.backup.exporter import BackupExporter
from src.backup.importer import BackupImporter

router = APIRouter()

# Global instances
agent = UNEXAgent()
voice_controller = VoiceController(agent)
audit_logger = AuditLogger()
app_catalog = ApplicationCatalog()
edu_manager = EducationManager()
vision_manager = VisionManager()
workflow = WorkflowEngine()

_rag_manager = None
def get_rag_manager() -> RAGManager:
    global _rag_manager
    if _rag_manager is None:
        _rag_manager = RAGManager()
    return _rag_manager

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await agent.chat(user_input=request.message, history=request.history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Memory Dashboard API ---

@router.get("/memory")
def get_all_memories():
    return agent.memory_manager.store.get_all_memories()

@router.get("/memory/search")
def search_memory(q: str):
    results = agent.memory_manager.search_memory(q)
    return [{"memory": mem, "score": score} for mem, score in results]

@router.get("/memory/projects")
def get_projects():
    return agent.memory_manager.store.get_all_memories(memory_type=MemoryType.PROJECT)

@router.get("/memory/preferences")
def get_preferences():
    return agent.memory_manager.store.get_all_memories(memory_type=MemoryType.PREFERENCE)

@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: str):
    agent.memory_manager.delete_memory(memory_id)
    return {"status": "success", "deleted_id": memory_id}

# --- Voice Diagnostics API ---

@router.get("/voice/status")
def get_voice_status():
    return voice_controller.get_diagnostics()

# --- Security & Monitor APIs ---

@router.get("/applications")
def get_applications():
    return {"applications": app_catalog.apps}

@router.get("/audit/logs")
def get_audit_logs(limit: int = 50):
    return {"logs": audit_logger.get_recent_logs(limit)}

@router.get("/permissions")
def get_permissions():
    from src.security.risk_classifier import RiskClassifier
    return {
        "risk_levels": [level.value for level in RiskLevel],
        "tool_risks": {k: v.value for k, v in RiskClassifier.TOOL_RISK_MAP.items()}
    }

# --- Education APIs ---

from fastapi import UploadFile, File

@router.post("/education/pdf-to-json")
async def pdf_to_json(file: UploadFile = File(...)):
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
        
    try:
        json_data = await edu_manager.process_pdf(tmp_path)
        return json_data.model_dump()
    finally:
        os.unlink(tmp_path)

@router.post("/education/analyze")
async def analyze_paper(file: UploadFile = File(...)):
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
        
    try:
        json_data = await edu_manager.process_pdf(tmp_path)
        analysis = PaperAnalyzer.analyze(json_data)
        return analysis
    finally:
        os.unlink(tmp_path)

# --- Vision APIs ---

@router.post("/vision/analyze-screen")
async def api_analyze_screen(region: str = "fullscreen"):
    result = await vision_manager.analyze_screen(region)
    return result

@router.post("/vision/extract-text")
def api_extract_text_screen():
    text = vision_manager.extract_text_from_screen()
    return {"text": text}

@router.post("/vision/analyze-image")
async def api_analyze_image(file: UploadFile = File(...)):
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
        
    try:
        result = await vision_manager.analyze_image_file(tmp_path)
        return result
    finally:
        os.unlink(tmp_path)

# --- RAG & Automation APIs ---

@router.post("/knowledge/index")
async def api_index_document(file: UploadFile = File(...)):
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
        
    try:
        await get_rag_manager().index_file(tmp_path, source_metadata={"filename": file.filename})
        return {"status": "Indexed", "filename": file.filename}
    finally:
        os.unlink(tmp_path)

@router.get("/knowledge/search")
async def api_search_knowledge(query: str):
    results = await get_rag_manager().search(query)
    return {"query": query, "results": results}

@router.post("/automation/schedule")
def api_schedule_task(prompt: str, interval_minutes: int):
    job_id = workflow.schedule_agent_task(prompt, interval_minutes)
    return {"status": "Scheduled", "job_id": job_id}

@router.post("/automation/watch-folder")
def api_watch_folder(folder_path: str):
    watch_id = workflow.monitor_and_index(folder_path)
    return {"status": "Watching", "watch_id": watch_id}

# --- Administration APIs ---

@router.get("/health")
def api_health():
    return {"status": "OK"}

@router.get("/metrics")
def api_metrics():
    return SystemMetrics.get_snapshot()

@router.get("/diagnostics")
async def api_diagnostics():
    return await DiagnosticsEngine.run_full_diagnostics()

@router.post("/system/backup")
def api_backup():
    try:
        path = BackupExporter.create_backup()
        return {"status": "Backup Created", "path": path}
    except Exception as e:
        return {"status": "Backup Failed", "error": str(e)}

@router.post("/system/restore")
def api_restore(zip_path: str):
    success = BackupImporter.restore_backup(zip_path)
    return {"status": "Success" if success else "Failed"}




