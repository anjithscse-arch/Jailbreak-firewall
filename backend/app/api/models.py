"""Model lifecycle and metadata API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.model_metadata import ModelMetadata
from app.models.user import User
from app.dependencies import get_admin_user
from app.schemas.common import ApiResponse
from app.services.ml_classifier_service import ml_classifier_service
from app.ml.train import train_model

router = APIRouter(prefix="/api/models", tags=["Model Lifecycle"])


@router.get("", summary="List model versions")
async def list_models(db: Session = Depends(get_db)):
    """List trained classifier iterations and accuracy metrics."""
    models = db.query(ModelMetadata).order_by(ModelMetadata.id.desc()).all()
    return ApiResponse(success=True, data=models)


@router.get("/active", summary="Get active model details")
async def get_active_model(db: Session = Depends(get_db)):
    """Retrieve metadata of the currently running Layer 2 ML model."""
    meta = ml_classifier_service.get_metadata()
    return ApiResponse(success=True, data=meta)


from app.services.continuous_learning_service import continuous_learning_service

@router.post("/retrain", summary="Trigger model retraining")
async def retrain_active_model(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Trigger training pipeline on latest dataset and update active model weights."""
    metadata = train_model()
    ml_classifier_service.reload()

    # Record in database
    record = ModelMetadata(
        model_name=metadata.get("model_name", "TFIDF-LogReg-Firewall-Classifier"),
        model_type=metadata.get("model_type", "tfidf-logreg"),
        version=metadata.get("version", "v1"),
        accuracy=metadata.get("accuracy"),
        precision=metadata.get("macro_precision"),
        recall=metadata.get("macro_recall"),
        f1_score=metadata.get("macro_f1"),
        artifact_path="app/ml/artifacts",
        active=True,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ApiResponse(
        success=True,
        message="Model retrained and reloaded successfully",
        data=metadata,
    )


@router.post("/learn-new-attacks", summary="Continuous Learning Loop: Retrain model on newly logged attacks")
async def learn_new_attacks(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Adaptive feedback loop: retrain ML classifier on captured attacks from Security Database."""
    meta = continuous_learning_service.retrain_from_security_database(db=db)
    return ApiResponse(
        success=True,
        message="Continuous Learning Loop completed: Model retrained on newly captured attacks!",
        data=meta,
    )

