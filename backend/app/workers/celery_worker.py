from celery import Celery
import os
import hashlib
from ..database.mysql import SessionLocal
from ..database import models
from ..services.scanner import BlockScanner
from ..services.entropy_profiler import EntropyProfiler
from ..services.fragment_classifier import FragmentClassifier
from ..services.reassembly_engine import ReassemblyEngine
from ..services.generative_repair import GenerativeRepair

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


@celery_app.task(name="compute_hash")
def compute_hash(image_id: int):
    """
    Background task to calculate SHA256 hash of a disk image.
    Ensures forensic integrity as required by PRD 9.
    """
    db = SessionLocal()
    try:
        db_image = (
            db.query(models.DiskImage).filter(models.DiskImage.id == image_id).first()
        )
        if not db_image or not os.path.exists(db_image.file_path):
            return f"Error: Disk image {image_id} not found at {db_image.file_path if db_image else 'N/A'}."

        sha256_hash = hashlib.sha256()
        with open(db_image.file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        db_image.hash_sha256 = sha256_hash.hexdigest()
        db.commit()
        return f"Hash computed for image {image_id}: {db_image.hash_sha256}"
    except Exception as e:
        return f"Error computing hash: {str(e)}"
    finally:
        db.close()


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

        # Initialize services
        scanner = BlockScanner()
        profiler = EntropyProfiler()
        classifier = FragmentClassifier()
        engine = ReassemblyEngine()
        repair_module = GenerativeRepair()

        # Step 1: Scan
        fragments_raw = scanner.scan_image(db_image.file_path)

        db_image.status = "classifying"
        db.commit()

        # Prepare fragments for classification and storage
        fragments_objects = []
        fragments_for_reassembly = []

        for offset, data in fragments_raw:
            # Step 2: Entropy Profiling
            entropy_score = profiler.calculate_entropy(data)

            # Step 3: AI Classification
            prediction = classifier.classify_fragment(data)

            # Create DB entry for fragment
            fragment = models.Fragment(
                disk_image_id=image_id,
                offset=offset,
                block_size=len(data),
                entropy=entropy_score,
                fragment_hash=hashlib.sha256(data).hexdigest(),
                classification=prediction["predicted_type"],
                confidence=prediction["confidence"],
            )
            fragments_objects.append(fragment)

            # Prepare data for reassembly engine
            fragments_for_reassembly.append(
                {
                    "offset": offset,
                    "data": data,
                    "identification": {
                        "type": prediction["predicted_type"].lower(),
                        "source": "ai" if prediction["confidence"] > 0.8 else "entropy",
                    },
                }
            )

        # Batch insert fragments
        db.add_all(fragments_objects)
        db.commit()

        # Update status
        db_image.status = "reassembling"
        db.commit()

        # Step 4: Reassembly
        # The reassembly engine sequences and recovers files
        sessions = engine.sequence_fragments(fragments_for_reassembly)

        for session in sessions:
            if not session["data"]:
                continue

            # Reconstruct and optionally repair/denoise
            final_data = engine.reconstruct_file([session])

            # Step 5: Generative Repair & Enhancement
            final_data = repair_module.reconstruct_header(session["type"], final_data)
            final_data = repair_module.inpaint_binary(final_data)
            final_data = repair_module.enhance_image(session["type"], final_data)

            # Save recovered file
            recovered_filename = (
                f"recovered_{image_id}_{session['id']}.{session['type']}"
            )
            recovered_dir = os.path.join("evidence", "recovered")
            os.makedirs(recovered_dir, exist_ok=True)
            recovered_path = os.path.join(recovered_dir, recovered_filename)

            with open(recovered_path, "wb") as f:
                f.write(final_data)

            # Store metadata for reconstructed file
            reconstructed_file = models.ReconstructedFile(
                disk_image_id=image_id,
                file_type=session["type"],
                confidence_score=0.9,  # Placeholder for overall session confidence
                recovered_path=recovered_path,
                file_size=len(final_data),
                recovery_status="completed",
            )
            db.add(reconstructed_file)

        # Final Status
        db_image.status = "completed"
        db.commit()

        # Add a forensic log entry for chain-of-custody
        log = models.ForensicLog(
            operation="full_recovery_completed",
            model_version="v1.0.0",
            parameters={
                "image_id": image_id,
                "fragments_processed": len(fragments_raw),
            },
            investigator="System Worker",
        )
        db.add(log)
        db.commit()

        return (
            f"Recovery for image {image_id} completed. {len(sessions)} files recovered."
        )

    except Exception as e:
        if db_image:
            db_image.status = "failed"
            db.commit()
        return f"Error processing recovery: {str(e)}"
    finally:
        db.close()
