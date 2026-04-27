"""
CLEATI V3.3 Production API - I18n Integrated Version
REST API orchestrating all intelligent engines with complete internationalization
Production-ready with strict language isolation
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
from typing import Dict, Any, Optional, List
import asyncio
import os
from datetime import datetime

# I18n imports
from cleati.i18n import (
    get_i18n_service,
    I18nMiddleware,
    I18nResponse,
    I18nReportsGenerator,
    get_i18n_context,
    get_request_language
)

from cleati_orchestrator_v3 import orchestrator, EventType
from cleati_reports_generator_v3 import ReportGenerator

# ============================================
# INITIALIZATION
# ============================================

# Initialize FastAPI app
app = FastAPI(
    title="CLEATI V3.3",
    description="Intelligent Business Plan + Green Finance + Monitoring Platform",
    version="3.3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize I18n
i18n = get_i18n_service(i18n_dir=os.path.join(os.path.dirname(__file__), 'cleati', 'i18n'))

# Add I18n Middleware
app.add_middleware(I18nMiddleware, i18n_service=i18n)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-Language"],
)

# Initialize reports generator with i18n
base_generator = ReportGenerator()
i18n_reports = I18nReportsGenerator(i18n, base_generator)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Validate i18n system on startup."""
    print("🌍 Initializing I18n System...")

    # Validate language isolation
    issues = i18n.validate_language_isolation()
    if issues:
        print(f"⚠️  Language mixing detected: {issues}")

    # Validate translation completeness
    missing = i18n.validate_translation_completeness()
    if missing:
        print(f"⚠️  Missing translations: {missing}")

    # Report supported languages
    languages = i18n.get_supported_languages()
    print(f"✓ I18n initialized with {len(languages)} languages")
    for lang in languages:
        print(f"  - {lang['code'].upper()}: {lang['nativeName']}")

    print("✓ CLEATI V3.3 API ready for multi-language support")


# ============================================
# PROJECT ENDPOINTS
# ============================================

@app.post("/api/v3/project/create")
async def create_project(request: Request, data: Dict[str, Any]):
    """
    Create a new project with i18n support

    Language: Provide via X-Language header or language query param
    """
    try:
        response = I18nResponse(request, data)

        # Validate required fields
        required_fields = ['name', 'budget', 'duration']
        for field in required_fields:
            if field not in data:
                return JSONResponse(
                    status_code=400,
                    content=response.error(
                        'missing_required_field',
                        'api',
                        status_code=400
                    )
                )

        # Create project
        project_id = orchestrator.create_project(data)

        # Log event
        orchestrator.log_event(
            project_id,
            EventType.PROJECT_CREATED,
            {"name": data.get('name')}
        )

        return response.success(
            'project_created',
            'api',
            project_id=project_id,
            metadata=orchestrator.projects[project_id].metadata
        )

    except Exception as e:
        response = I18nResponse(request)
        return JSONResponse(
            status_code=500,
            content=response.error('error_creating_project', 'api', status_code=500)
        )


@app.post("/api/v3/project/{project_id}/process")
async def process_full_pipeline(
    request: Request,
    project_id: str,
    user_answers: Dict[str, Any]
):
    """
    Process complete pipeline with full localization
    1. Financial Analysis
    2. Green Impact Analysis
    3. Business Plan Generation
    4. Monitoring & Evaluation Plan
    5. Integrity Validation
    """
    try:
        response = I18nResponse(request)

        if project_id not in orchestrator.projects:
            return JSONResponse(
                status_code=404,
                content=response.error('project_not_found', 'api', status_code=404)
            )

        # Process pipeline
        result = await orchestrator.process_full_pipeline(project_id, user_answers)

        return response.success(
            'financial_analysis_complete',
            'api',
            project_id=project_id,
            results=result
        )

    except Exception as e:
        response = I18nResponse(request)
        return JSONResponse(
            status_code=500,
            content=response.error('server_error', 'api', status_code=500)
        )


@app.get("/api/v3/project/{project_id}")
async def get_project(request: Request, project_id: str):
    """Get complete project data with localization"""
    try:
        response = I18nResponse(request)

        if project_id not in orchestrator.projects:
            return JSONResponse(
                status_code=404,
                content=response.error('project_not_found', 'api', status_code=404)
            )

        unified = orchestrator.projects[project_id]

        return response.success(
            'success',  # Generic success for data endpoint
            'api',
            project_id=project_id,
            data=unified.to_dict()
        )

    except Exception as e:
        response = I18nResponse(request)
        return JSONResponse(
            status_code=500,
            content=response.error('server_error', 'api', status_code=500)
        )


@app.get("/api/v3/project/{project_id}/status")
async def get_project_status(request: Request, project_id: str):
    """Get localized project status"""
    try:
        response = I18nResponse(request)

        if project_id not in orchestrator.projects:
            return JSONResponse(
                status_code=404,
                content=response.error('project_not_found', 'api', status_code=404)
            )

        unified = orchestrator.projects[project_id]

        completion = {
            response.translate('financial', 'ui'): len(unified.financial_data) > 0,
            response.translate('green', 'ui'): len(unified.green_metrics) > 0,
            response.translate('business_plan', 'ui'): len(unified.business_plan) > 0,
            response.translate('monitoring', 'ui'): len(unified.monitoring_plan) > 0,
        }

        return {
            "status": "success",
            "project_id": project_id,
            "completion": completion,
            "ready_for_reports": all(completion.values()),
            "language": get_request_language(request)
        }

    except Exception as e:
        response = I18nResponse(request)
        return JSONResponse(
            status_code=500,
            content=response.error('server_error', 'api', status_code=500)
        )


# ============================================
# REPORT ENDPOINTS - FULLY LOCALIZED
# ============================================

@app.post("/api/v3/project/{project_id}/report")
async def generate_report(
    request: Request,
    project_id: str,
    formats: Optional[List[str]] = None,
    language: Optional[str] = None
):
    """
    Generate localized reports in requested formats

    Parameters:
    - formats: ['pdf', 'excel', 'word'] (default: all)
    - language: Language code (default: request language)

    Example:
        POST /api/v3/project/123/report?language=fr
        {
            "formats": ["pdf", "excel"]
        }
    """
    try:
        response = I18nResponse(request)

        if project_id not in orchestrator.projects:
            return JSONResponse(
                status_code=404,
                content=response.error('project_not_found', 'api', status_code=404)
            )

        # Use specified language or request language
        report_language = language or get_request_language(request)

        # Validate language
        if not i18n.set_language(report_language):
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Language '{report_language}' not supported",
                    "supported_languages": [l['code'] for l in i18n.get_supported_languages()],
                    "language": get_request_language(request)
                }
            )

        # Get project data
        unified = orchestrator.projects[project_id]
        project_data = unified.to_dict()

        # Generate reports
        if formats is None:
            formats = ['pdf', 'excel', 'word']

        reports = i18n_reports.generate_all_formats(
            project_data,
            formats=formats,
            language=report_language
        )

        # Log event
        orchestrator.log_event(
            project_id,
            EventType.REPORT_GENERATED,
            {"formats": formats, "language": report_language}
        )

        return {
            "status": "success",
            "message": response.translate('report_generated', 'api'),
            "project_id": project_id,
            "language": report_language,
            "formats_generated": list(reports.keys()),
            "download_endpoints": {
                fmt: f"/api/v3/project/{project_id}/report/{fmt}?language={report_language}"
                for fmt in reports.keys()
            }
        }

    except Exception as e:
        response = I18nResponse(request)
        return JSONResponse(
            status_code=500,
            content=response.error('error_generating_report', 'api', status_code=500)
        )


@app.get("/api/v3/project/{project_id}/report/{format}")
async def download_report(
    request: Request,
    project_id: str,
    format: str,
    language: Optional[str] = None
):
    """Download specific report format"""
    try:
        if project_id not in orchestrator.projects:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get project data
        unified = orchestrator.projects[project_id]
        project_data = unified.to_dict()

        # Generate report in requested language
        report_language = language or get_request_language(request)

        reports = i18n_reports.generate_all_formats(
            project_data,
            formats=[format],
            language=report_language
        )

        if format not in reports:
            raise HTTPException(status_code=400, detail=f"Format '{format}' not supported")

        # Return appropriate media type
        media_type_map = {
            'pdf': 'application/pdf',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'word': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }

        return FileResponse(
            path=reports[format],
            media_type=media_type_map.get(format, 'application/octet-stream'),
            filename=f"CLEATI_Report_{project_id}_{report_language}.{format}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ANALYSIS ENDPOINTS
# ============================================

@app.post("/api/v3/project/{project_id}/analyze/financial")
async def analyze_financial(request: Request, project_id: str, data: Dict[str, Any]):
    """Run financial analysis with localized results"""
    try:
        response = I18nResponse(request)

        if project_id not in orchestrator.projects:
            return JSONResponse(
                status_code=404,
                content=response.error('project_not_found', 'api', status_code=404)
            )

        # Run analysis
        result = await orchestrator.run_financial_analysis(project_id, data)

        orchestrator.log_event(
            project_id,
            EventType.FINANCIAL_ANALYSIS_COMPLETE,
            result
        )

        return response.success(
            'financial_analysis_complete',
            'api',
            project_id=project_id,
            analysis=result
        )

    except Exception as e:
        response = I18nResponse(request)
        return JSONResponse(
            status_code=500,
            content=response.error('error_analyzing_financial', 'api', status_code=500)
        )


@app.post("/api/v3/project/{project_id}/analyze/green")
async def analyze_green(request: Request, project_id: str, data: Dict[str, Any]):
    """Run green impact analysis with localized results"""
    try:
        response = I18nResponse(request)

        if project_id not in orchestrator.projects:
            return JSONResponse(
                status_code=404,
                content=response.error('project_not_found', 'api', status_code=404)
            )

        # Run analysis
        result = await orchestrator.run_green_analysis(project_id, data)

        orchestrator.log_event(
            project_id,
            EventType.GREEN_ANALYSIS_COMPLETE,
            result
        )

        return response.success(
            'green_analysis_complete',
            'api',
            project_id=project_id,
            analysis=result
        )

    except Exception as e:
        response = I18nResponse(request)
        return JSONResponse(
            status_code=500,
            content=response.error('error_analyzing_green', 'api', status_code=500)
        )


# ============================================
# HEALTH & SYSTEM ENDPOINTS
# ============================================

@app.get("/api/v3/health")
async def health_check(request: Request):
    """Health check with localization info"""
    response = I18nResponse(request)

    languages = i18n.get_supported_languages()
    current_language = get_request_language(request)

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.3.0",
        "i18n": {
            "current_language": current_language,
            "supported_languages": [l['code'] for l in languages],
            "total_languages": len(languages)
        },
        "projects_loaded": len(orchestrator.projects),
        "message": response.translate('welcome', 'common')
    }


@app.get("/api/v3/languages")
async def get_languages(request: Request):
    """Get list of supported languages and locales"""
    languages = i18n.get_supported_languages()
    current_lang = get_request_language(request)

    return {
        "status": "success",
        "current_language": current_lang,
        "supported_languages": languages,
        "total": len(languages)
    }


@app.get("/api/v3/config")
async def get_config(request: Request):
    """Get API configuration with localization settings"""
    current_lang = get_request_language(request)
    locale_config = i18n.get_locale_config(current_lang)

    return {
        "status": "success",
        "api_version": "3.3.0",
        "current_language": current_lang,
        "locale_config": locale_config,
        "supported_languages": [l['code'] for l in i18n.get_supported_languages()],
        "features": {
            "multi_language": True,
            "financial_analysis": True,
            "green_impact": True,
            "business_planning": True,
            "monitoring_evaluation": True,
            "report_generation": True,
            "pdf_export": True,
            "excel_export": True,
            "word_export": True
        }
    }


# ============================================
# ERROR HANDLERS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with localization"""
    response = I18nResponse(request)

    # Try to translate detail if it's a known key
    detail = exc.detail
    if isinstance(detail, str) and detail.startswith('ERROR_'):
        detail = response.translate(detail, 'api')

    return {
        "status": "error",
        "code": exc.status_code,
        "message": detail,
        "language": get_request_language(request)
    }


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with localization"""
    response = I18nResponse(request)

    return {
        "status": "error",
        "code": 500,
        "message": response.translate('server_error', 'api'),
        "language": get_request_language(request)
    }


# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
async def root(request: Request):
    """Root endpoint with welcome message in user's language"""
    response = I18nResponse(request)
    language = get_request_language(request)

    return {
        "status": "success",
        "message": response.translate('welcome', 'common'),
        "app_name": response.translate('app_name', 'common'),
        "version": "3.3.0",
        "language": language,
        "api_docs": "/docs",
        "endpoints": {
            "health": "/api/v3/health",
            "languages": "/api/v3/languages",
            "config": "/api/v3/config",
            "project_create": "/api/v3/project/create",
            "project_get": "/api/v3/project/{project_id}",
            "project_status": "/api/v3/project/{project_id}/status",
            "project_analyze": "/api/v3/project/{project_id}/analyze",
            "project_report": "/api/v3/project/{project_id}/report"
        }
    }


# ============================================
# STATIC FILES (Optional)
# ============================================

# Uncomment to serve static files
# app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn

    # Run with language support
    print("🚀 Starting CLEATI V3.3 API with Multi-Language Support")
    print("📚 Documentation available at: http://localhost:8000/docs")
    print("🌍 Languages supported: FR, EN, ES, DE, IT, PT, NL, PL")
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
