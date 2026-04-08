"""
Office Suite API Routes - Complete with Conversion, Translation, Resume & Invoice Builders
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from app.document_processor.office_editor import office_editor
from app.api.dependencies.auth import get_current_user

router = APIRouter()


class DocumentCreate(BaseModel):
    title: str
    author: Optional[str] = None
    content: Dict[str, Any]
    format: str = "docx"


# ============================================================================
# INFO & TEST ENDPOINTS
# ============================================================================

@router.get("/test")
async def test():
    return {"message": "Office router works!", "status": "ok"}


@router.get("/ping")
async def ping():
    return {"ping": "pong", "router": "office"}


@router.get("/info")
async def office_info():
    return {
        "name": "DarkmoorAI Office Suite",
        "version": "3.0.0",
        "description": "Free office document creation, editing, conversion, translation, resume & invoice builder",
        "features": {
            "word": {"create": True, "edit": True, "templates": ["invoice", "report", "resume", "business_letter"], "formats": [".docx", ".pdf", ".txt"]},
            "excel": {"create": True, "edit": True, "formulas": True, "charts": ["bar", "line", "pie"], "templates": ["budget"], "formats": [".xlsx", ".csv"]},
            "powerpoint": {"create": True, "formats": [".pptx"]},
            "conversion": {"from": [".pdf", ".docx", ".xlsx", ".pptx", ".csv", ".txt"], "to": [".docx", ".xlsx", ".csv", ".txt", ".pdf"]},
            "translation": {"supported_formats": ["txt", "docx", "pdf", "xlsx", "pptx"], "languages": 11},
            "resume_builder": {"templates": ["modern", "classic", "creative", "executive", "tech"], "features": ["photo upload", "skills rating", "achievements"]},
            "invoice_builder": {"templates": ["professional", "modern", "minimal", "corporate", "simple"], "features": ["logo upload", "QR code", "tax calculation", "bank details"]}
        },
        "cost": "Free",
        "status": "active"
    }


# ============================================================================
# RESUME BUILDER ENDPOINTS
# ============================================================================

@router.post("/resume/enhanced")
async def create_enhanced_resume(
    data: Dict[str, Any],
    template: str = "modern",
    current_user: dict = Depends(get_current_user)
):
    """Create professional resume with photo. Templates: modern, classic, creative, executive, tech"""
    try:
        filepath = office_editor.create_resume_with_template(data, template)
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=Path(filepath).name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resume/templates")
async def get_resume_templates(current_user: dict = Depends(get_current_user)):
    return {
        "templates": [
            {"id": "modern", "name": "Modern", "description": "Clean two-column layout with sidebar"},
            {"id": "classic", "name": "Classic", "description": "Traditional professional layout"},
            {"id": "creative", "name": "Creative", "description": "Design-focused with color accents"},
            {"id": "executive", "name": "Executive", "description": "Leadership-focused layout"},
            {"id": "tech", "name": "Tech/IT", "description": "Technology-focused with skills categories"}
        ],
        "features": ["Photo upload support", "Skills rating bars", "Achievements with metrics", "Project links", "Multiple formatting options"]
    }


# ============================================================================
# INVOICE BUILDER ENDPOINTS
# ============================================================================

@router.post("/invoice/enhanced")
async def create_enhanced_invoice(
    data: Dict[str, Any],
    template: str = "professional",
    current_user: dict = Depends(get_current_user)
):
    """Create professional invoice with company logo. Templates: professional, modern, minimal, corporate, simple"""
    try:
        filepath = office_editor.create_invoice_with_template(data, template)
        return FileResponse(
            filepath,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=Path(filepath).name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoice/templates")
async def get_invoice_templates(current_user: dict = Depends(get_current_user)):
    return {
        "templates": [
            {"id": "professional", "name": "Professional", "description": "Full-featured with logo, bank details, QR"},
            {"id": "modern", "name": "Modern", "description": "Colorful and contemporary"},
            {"id": "minimal", "name": "Minimal", "description": "Clean and simple"},
            {"id": "corporate", "name": "Corporate", "description": "Business formal"},
            {"id": "simple", "name": "Simple", "description": "Basic invoice"}
        ],
        "features": ["Company logo upload", "QR code for payments", "Multiple tax rates", "Payment terms", "Bank details section", "Custom notes"]
    }


# ============================================================================
# TRADITIONAL TEMPLATE ENDPOINTS (Legacy)
# ============================================================================

@router.post("/template/resume")
async def create_resume(data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Legacy resume creation (use /resume/enhanced for new features)"""
    try:
        filepath = office_editor.create_resume_with_template(data, "classic")
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=Path(filepath).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/template/invoice")
async def create_invoice(data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Legacy invoice creation (use /invoice/enhanced for new features)"""
    try:
        filepath = office_editor.create_invoice_with_template(data, "professional")
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=Path(filepath).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/template/report")
async def create_report(data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Create a report document"""
    try:
        filepath = office_editor.create_word_document(data, f"report_{data.get('title', 'report')}.docx")
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=Path(filepath).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/template/business_letter")
async def create_business_letter(data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Create a business letter"""
    try:
        filepath = office_editor.create_word_document(data, f"letter_{data.get('subject', 'letter')}.docx")
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=Path(filepath).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/template/budget")
async def create_budget(data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    """Create a budget spreadsheet"""
    try:
        filepath = office_editor.create_excel_document(data, f"budget_{data.get('name', 'budget')}.xlsx")
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=Path(filepath).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DOCUMENT CREATION ENDPOINTS
# ============================================================================

@router.post("/word/create")
async def create_word_document(data: DocumentCreate, current_user: dict = Depends(get_current_user)):
    try:
        filename = f"document_{data.title.replace(' ', '_')}.{data.format}"
        filepath = office_editor.create_word_document(data.content, filename)
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/excel/create")
async def create_excel_document(data: DocumentCreate, current_user: dict = Depends(get_current_user)):
    try:
        filename = f"spreadsheet_{data.title.replace(' ', '_')}.xlsx"
        filepath = office_editor.create_excel_document(data.content, filename)
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/powerpoint/create")
async def create_powerpoint(data: DocumentCreate, current_user: dict = Depends(get_current_user)):
    try:
        filename = f"presentation_{data.title.replace(' ', '_')}.pptx"
        filepath = office_editor.create_powerpoint(data.content, filename)
        return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DOCUMENT CONVERSION ENDPOINTS
# ============================================================================

@router.post("/convert/smart")
async def smart_convert(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Smart document converter – auto-detects input format. Supported: pdf, docx, xlsx, pptx, csv, txt"""
    try:
        temp_path = office_editor.temp_dir / file.filename
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        output_path = office_editor.convert_document(str(temp_path), target_format)
        mime_types = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'csv': 'text/csv',
            'txt': 'text/plain',
        }
        return FileResponse(output_path, media_type=mime_types.get(target_format, 'application/octet-stream'), filename=Path(output_path).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.post("/convert")
async def convert_document(
    file: UploadFile = File(...),
    output_format: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Convert document between formats (Word, Excel, PDF, CSV, TXT)"""
    SUPPORTED_FORMATS = ['docx', 'xlsx', 'csv', 'txt', 'pdf']
    if output_format.lower() not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported output format. Supported: {SUPPORTED_FORMATS}")
    try:
        temp_path = office_editor.temp_dir / file.filename
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        output_path = office_editor.convert_document(str(temp_path), output_format)
        mime_types = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'csv': 'text/csv',
            'txt': 'text/plain',
        }
        return FileResponse(output_path, media_type=mime_types.get(output_format, 'application/octet-stream'), filename=f"{Path(file.filename).stem}.{output_format}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.post("/convert/batch")
async def batch_convert(
    files: List[UploadFile] = File(...),
    target_format: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Batch convert multiple documents"""
    try:
        temp_paths = []
        for file in files:
            temp_path = office_editor.temp_dir / file.filename
            content = await file.read()
            with open(temp_path, "wb") as f:
                f.write(content)
            temp_paths.append(str(temp_path))
        output_paths = await office_editor.batch_convert(temp_paths, target_format)
        if output_paths:
            return FileResponse(output_paths[0], filename=Path(output_paths[0]).name)
        else:
            raise HTTPException(status_code=400, detail="No files converted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in temp_paths:
            if Path(path).exists():
                Path(path).unlink()


# ============================================================================
# DOCUMENT TRANSLATION ENDPOINTS
# ============================================================================

@router.post("/translate")
async def translate_document(
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...),
    output_format: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Translate document from source language to target language. Supported languages: en, fr, es, de, it, pt, ru, zh, ja, ko, ar"""
    try:
        temp_path = office_editor.temp_dir / file.filename
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        output_path = await office_editor.translate_document(str(temp_path), source_lang, target_lang, output_format)
        return FileResponse(output_path, filename=Path(output_path).name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()


# ============================================================================
# SUPPORTED CONVERSIONS ENDPOINT
# ============================================================================

@router.get("/supported-conversions")
async def get_supported_conversions(current_user: dict = Depends(get_current_user)):
    return {
        "conversions": {
            "pdf": ["docx", "xlsx", "pptx"],
            "docx": ["pdf", "xlsx", "csv", "txt"],
            "xlsx": ["pdf", "csv", "docx"],
            "pptx": ["pdf", "docx"],
            "csv": ["xlsx"],
            "txt": ["docx", "pdf"]
        },
        "translation_supported_formats": ["txt", "docx", "pdf", "xlsx", "pptx"],
        "translation_languages": {
            "en": "English", "fr": "French", "es": "Spanish", "de": "German",
            "it": "Italian", "pt": "Portuguese", "ru": "Russian", "zh": "Chinese",
            "ja": "Japanese", "ko": "Korean", "ar": "Arabic"
        }
    }


# ============================================================================
# DOWNLOAD ENDPOINT
# ============================================================================

@router.get("/download/{file_id}")
async def download_document(file_id: str, current_user: dict = Depends(get_current_user)):
    temp_dir = office_editor.temp_dir
    for file in temp_dir.glob(f"{file_id}.*"):
        return FileResponse(str(file), filename=file.name)
    raise HTTPException(status_code=404, detail="File not found")