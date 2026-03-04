from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import mysql, models, schemas
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
    # Attempt to init DB, might fail if MySQL is not ready
    # mysql.init_db()
    pass


@app.get("/")
async def root():
    return {"message": "AI File Carving System API is running."}


@app.post("/api/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    investigation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(mysql.get_db),
):
    # Save file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store metadata in DB
    db_image = models.DiskImage(
        investigation_id=investigation_id,
        file_path=file_path,
        size=os.path.getsize(file_path),
        hash_sha256="pending",
        status="uploaded",
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return {"image_id": db_image.id, "status": "uploaded"}


@app.post("/api/recover/{image_id}")
async def start_recovery(image_id: int, db: Session = Depends(mysql.get_db)):
    db_image = (
        db.query(models.DiskImage).filter(models.DiskImage.id == image_id).first()
    )
    if not db_image:
        raise HTTPException(status_code=404, detail="Disk image not found")

    # Placeholder for Task Queue Trigger (Celery)
    task_id = f"recovery_{uuid.uuid4().hex[:8]}"
    db_image.status = "processing"
    db.commit()

    return {"task_id": task_id, "status": "processing"}


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
