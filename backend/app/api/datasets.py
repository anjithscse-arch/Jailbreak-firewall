"""Datasets management API router."""

import shutil
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.dependencies import get_admin_user
from app.schemas.common import ApiResponse
from app.services.dataset_service import dataset_service

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])


@router.get("", summary="List prompt datasets")
async def list_datasets(db: Session = Depends(get_db)):
    """Retrieve all uploaded and seeded training/evaluation datasets."""
    records = dataset_service.list_datasets(db)
    data = [
        {
            "id": r.id,
            "name": r.name,
            "filename": r.filename,
            "row_count": r.row_count,
            "validation_status": r.validation_status,
            "created_at": r.created_at,
        }
        for r in records
    ]
    return ApiResponse(success=True, data=data)


@router.post("/upload", summary="Upload custom dataset CSV")
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Upload a candidate prompt dataset in CSV format."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    uploads_dir = settings.BASE_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    target_path = uploads_dir / file.filename

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Validate structure
    val_report = dataset_service.validate_csv(target_path)
    status_str = "VALID" if val_report["is_valid"] else "INVALID"

    record = dataset_service.register_dataset(
        db=db,
        name=Path(file.filename).stem,
        filename=file.filename,
        row_count=val_report["row_count"],
        distribution=val_report["class_distribution"],
        status=status_str,
    )

    return ApiResponse(
        success=True,
        message="Dataset uploaded and validated successfully",
        data={
            "dataset_id": record.id,
            "name": record.name,
            "validation": val_report,
        },
    )


@router.post("/validate", summary="Validate local or uploaded CSV dataset")
async def validate_dataset(file: UploadFile = File(...)):
    """Dry-run validation of a dataset file without persisting."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    uploads_dir = settings.BASE_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    temp_path = uploads_dir / f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        report = dataset_service.validate_csv(temp_path)
        return ApiResponse(success=True, data=report)
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.delete("/{dataset_id}", summary="Delete dataset record")
async def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Delete a catalogued dataset record."""
    dataset_service.delete_dataset(db, dataset_id)
    return ApiResponse(success=True, message="Dataset deleted successfully", data=True)
