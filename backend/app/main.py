from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import mysql, models
from .workers.celery_worker import celery_app, process_recovery, compute_hash
from celery.result import AsyncResult
import os
import shutil
import uuid

app = FastAPI(
    title="AI File Carving System API",
    description="Backend for AI-Powered Autonomous File Carving and Reconstruction",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
RECOVERY_DIR = os.getenv("RECOVERY_DIR", "evidence/recovered")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RECOVERY_DIR, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    # Attempt to init DB
    mysql.init_db()


@app.get("/")
async def root():
    return {"message": "AI File Carving System API is running."}


@app.post("/api/investigations")
def create_investigation(
    case_name: str,
    investigator: str = None,
    description: str = None,
    db: Session = Depends(mysql.get_db),
):
    investigation = models.Investigation(
        case_name=case_name,
        investigator=investigator,
        description=description,
    )

    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    return investigation


@app.post("/api/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    investigation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(mysql.get_db),
):
    ALLOWED_EXTENSIONS = [".dd", ".img", ".raw", ".iso", ".e01"]
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid disk image format")

    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store metadata in DB
    db_image = models.DiskImage(
        investigation_id=investigation_id,
        file_path=os.path.abspath(file_path),
        size=os.path.getsize(file_path),
        hash_sha256="pending",
        status="uploaded",
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    # Trigger background hash calculation
    compute_hash.delay(db_image.id)

    return {"image_id": db_image.id, "status": "uploaded"}


@app.post("/api/recover/{image_id}")
async def start_recovery(image_id: int, db: Session = Depends(mysql.get_db)):
    db_image = (
        db.query(models.DiskImage).filter(models.DiskImage.id == image_id).first()
    )
    if not db_image:
        raise HTTPException(status_code=404, detail="Disk image not found")

    # Trigger background task with Celery
    task = process_recovery.delay(image_id)

    db_image.status = "processing"
    db.commit()

    return {"task_id": task.id, "status": "processing"}


@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Returns the current status of a background task.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
    }


@app.get("/api/fragments/{image_id}")
async def get_fragments(image_id: int, db: Session = Depends(mysql.get_db)):
    fragments = (
        db.query(models.Fragment)
        .filter(models.Fragment.disk_image_id == image_id)
        .all()
    )
    return fragments


@app.get("/api/recovered-files/{image_id}")
async def get_recovered_files(image_id: int, db: Session = Depends(mysql.get_db)):
    recovered_files = (
        db.query(models.ReconstructedFile)
        .filter(models.ReconstructedFile.disk_image_id == image_id)
        .all()
    )
    return recovered_files


@app.get("/api/download/{file_id}")
async def download_file(file_id: int, db: Session = Depends(mysql.get_db)):
    db_file = (
        db.query(models.ReconstructedFile)
        .filter(models.ReconstructedFile.id == file_id)
        .first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(db_file.recovered_path):
        raise HTTPException(status_code=404, detail="File content not found on server")

    from fastapi.responses import FileResponse

    return FileResponse(
        db_file.recovered_path, filename=f"recovered_{db_file.id}.{db_file.file_type}"
    )
