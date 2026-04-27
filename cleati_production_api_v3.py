"""
CLEATI V3.3 Production API
API REST pour orchestrer tous les moteurs intelligents
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from typing import Dict, Any
import asyncio

from cleati_orchestrator_v3 import orchestrator, EventType

app = FastAPI(
    title="CLEATI V3.3",
    description="Intelligent Business Plan + Green Finance + Monitoring Platform",
    version="3.3.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CONVERSATION ENDPOINTS
# ============================================

@app.post("/api/v3/project/create")
async def create_project(data: Dict[str, Any]):
    """Crée un nouveau projet"""
    try:
        project_id = orchestrator.create_project(data)
        return {
            "status": "success",
            "project_id": project_id,
            "message": f"Project {project_id} created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/project/{project_id}/process")
async def process_full_pipeline(project_id: str, user_answers: Dict[str, Any]):
    """
    Lance le pipeline complet:
    1. Analyse Financière
    2. Analyse Verte
    3. Génération Business Plan
    4. Auto-génération Plan S&E
    5. Validation d'intégrité
    """
    try:
        result = await orchestrator.process_full_pipeline(project_id, user_answers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/project/{project_id}/status")
async def get_project_status(project_id: str):
    """Récupère le statut du projet"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        unified = orchestrator.projects[project_id]
        return {
            "project_id": project_id,
            "metadata": unified.metadata,
            "completion": {
                "financial": len(unified.financial_data) > 0,
                "green": len(unified.green_metrics) > 0,
                "business_plan": len(unified.business_plan) > 0,
                "monitoring": len(unified.monitoring_plan) > 0
            },
            "ready_for_reports": all([
                len(unified.financial_data) > 0,
                len(unified.green_metrics) > 0,
                len(unified.business_plan) > 0,
                len(unified.monitoring_plan) > 0
            ])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/project/{project_id}/data")
async def get_project_unified_data(project_id: str):
    """Récupère les données unifiées du projet"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        unified = orchestrator.projects[project_id]
        return unified.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/project/{project_id}/integrity")
async def check_integrity(project_id: str):
    """Vérifie l'intégrité inter-modules"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        unified = orchestrator.projects[project_id]
        return unified.validate_integrity()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/project/{project_id}/events")
async def get_project_events(project_id: str):
    """Récupère les événements du projet"""
    try:
        filtered_events = [e for e in orchestrator.events if e["project_id"] == project_id]
        return {
            "project_id": project_id,
            "events": filtered_events,
            "count": len(filtered_events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/project/{project_id}/reset")
async def reset_project(project_id: str):
    """Réinitialise un projet"""
    try:
        if project_id in orchestrator.projects:
            del orchestrator.projects[project_id]
        return {"status": "success", "message": "Project reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# FINANCIAL ENDPOINTS
# ============================================

@app.get("/api/v3/project/{project_id}/financial")
async def get_financial_data(project_id: str):
    """Récupère les données financières"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "project_id": project_id,
            "financial_data": orchestrator.projects[project_id].financial_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# GREEN ENDPOINTS
# ============================================

@app.get("/api/v3/project/{project_id}/green")
async def get_green_metrics(project_id: str):
    """Récupère les métriques vertes"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        unified = orchestrator.projects[project_id]
        return {
            "project_id": project_id,
            "green_metrics": unified.green_metrics,
            "funding_sources": unified.funding_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# BUSINESS PLAN ENDPOINTS
# ============================================

@app.get("/api/v3/project/{project_id}/business-plan")
async def get_business_plan(project_id: str):
    """Récupère le business plan"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "project_id": project_id,
            "business_plan": orchestrator.projects[project_id].business_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# MONITORING & EVALUATION ENDPOINTS
# ============================================

@app.get("/api/v3/project/{project_id}/monitoring")
async def get_monitoring_plan(project_id: str):
    """Récupère le plan de suivi & évaluation"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        return {
            "project_id": project_id,
            "monitoring_plan": orchestrator.projects[project_id].monitoring_plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/project/{project_id}/monitoring/update")
async def update_monitoring_data(project_id: str, actual_data: Dict[str, Any]):
    """Met à jour les données réelles vs projections pour le suivi"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        unified = orchestrator.projects[project_id]
        monitoring = unified.monitoring_plan

        # Compare les données réelles aux cibles
        comparisons = []
        for kpi in monitoring.get("kpis", []):
            kpi_name = kpi.get("name")
            if kpi_name in actual_data:
                actual_value = actual_data[kpi_name]
                target_value = kpi.get("target")
                variance = (actual_value / target_value - 1) * 100 if target_value > 0 else 0

                alert = variance < (kpi.get("alert_threshold", 0.8) - 1) * 100

                comparisons.append({
                    "kpi": kpi_name,
                    "target": target_value,
                    "actual": actual_value,
                    "variance_percent": round(variance, 2),
                    "status": "ALERT" if alert else "OK",
                    "on_track": not alert
                })

        return {
            "project_id": project_id,
            "comparison_timestamp": "2026-04-26",
            "comparisons": comparisons
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HEALTH & INFO
# ============================================

@app.get("/api/v3/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.3.0",
        "projects_active": len(orchestrator.projects),
        "events_logged": len(orchestrator.events)
    }

@app.get("/api/v3/info")
async def get_info():
    """Informations sur CLEATI V3.3"""
    return {
        "name": "CLEATI V3.3",
        "description": "Intelligent Business Plan + Green Finance + Monitoring Platform",
        "version": "3.3.0",
        "modules": [
            "Financial Intelligence Engine",
            "Green Impact Intelligence Engine",
            "Business Plan Architect",
            "Monitoring & Evaluation Auto-Architect"
        ],
        "features": [
            "Unified Data Model (Single Source of Truth)",
            "Event-Driven Architecture",
            "Auto-Generated Business Plans",
            "Auto-Generated Monitoring Plans",
            "Intelligent Funding Source Matching",
            "Inter-Module Integrity Validation",
            "Dual ROI Calculation (Financial + Ecological)",
            "Automatic KPI Generation",
            "Green Finance Eligibility Assessment"
        ]
    }

# ============================================
# ROOT
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CLEATI V3.3",
        "version": "3.3.0",
        "endpoints": "/api/v3/info"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
