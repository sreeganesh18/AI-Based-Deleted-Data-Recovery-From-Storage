from celery import Celery
import os
from ..database.mysql import SessionLocal
from ..database import models
from ..services.scanner import BlockScanner
from ..services.entropy_profiler import EntropyProfiler
from ..services.fragment_classifier import FragmentClassifier
from ..services.reassembly_engine import ReassemblyEngine

# Celery Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("forensic_tasks", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="process_recovery")
def process_recovery(image_id: int):
    """
    Main background task for file recovery.
    1. Scan disk image
    2. Profile entropy of fragments
    3. Classify fragments using AI
    4. Reassemble fragments into files
    """
    db = SessionLocal()
    try:
        # Get disk image metadata
        db_image = (
            db.query(models.DiskImage).filter(models.DiskImage.id == image_id).first()
        )
        if not db_image:
            return f"Error: Disk image {image_id} not found."

        db_image.status = "scanning"
        db.commit()

        # Step 1: Scan (Placeholder)
        scanner = BlockScanner()
        fragments_data = scanner.scan_image(db_image.file_path)

        # Step 2: Entropy Profiling (Placeholder)
        profiler = EntropyProfiler()
        # In a real impl, this would loop through fragments

        # Update status
        db_image.status = "classifying"
        db.commit()

        # Step 3: AI Classification (Placeholder)
        classifier = FragmentClassifier()
        # classifier.classify_fragments(fragments_data)

        # Update status
        db_image.status = "reassembling"
        db.commit()

        # Step 4: Reassembly (Placeholder)
        engine = ReassemblyEngine()
        # engine.reassemble(image_id)

        # Final Status
        db_image.status = "completed"
        db.commit()

        # Add a log entry
        log = models.ForensicLog(
            operation="full_recovery_completed",
            model_version="v1.0.0",
            parameters={"image_id": image_id},
            investigator="System Worker",
        )
        db.add(log)
        db.commit()

        return f"Recovery for image {image_id} completed successfully."

    except Exception as e:
        if db_image:
            db_image.status = "failed"
            db.commit()
        return f"Error processing recovery: {str(e)}"
    finally:
        db.close()
