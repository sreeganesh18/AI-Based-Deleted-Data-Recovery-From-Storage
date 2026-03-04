Your document already contains the **research + technical specification**. What you are missing for a college submission is the **software product layer**: backend architecture, API design, database schema, containerization, and deployment pipeline.

You explicitly said **“Do not remove anything.”**
So the correct approach is:

* **Keep your entire document unchanged**
* **Append new sections** that define the backend system implementation

Below is the **PRD extension** that converts your research specification into a **complete backend system specification using FastAPI + MySQL + Docker**.

---

# Backend System Architecture and PRD Extension

## AI-Powered Autonomous File Carving and Reconstruction System

*(This section must be appended after the Conclusion in your document. Nothing from the original text is removed.)*

---

# 1. System Backend Overview

The backend layer operationalizes the AI-powered file carving pipeline by exposing a modular API architecture capable of ingesting disk images, orchestrating AI classification pipelines, performing fragment reconstruction, and delivering reconstructed files to investigators.

The backend system is implemented using:

| Component          | Technology                                  |
| ------------------ | ------------------------------------------- |
| API Framework      | FastAPI                                     |
| AI Engine          | PyTorch                                     |
| Database           | MySQL                                       |
| Task Queue         | Celery + Redis                              |
| Containerization   | Docker                                      |
| Model Optimization | Intel Extension for PyTorch                 |
| Storage            | Local filesystem or mounted forensic volume |

The architecture separates concerns into four major services:

1. **API Gateway**
2. **AI Processing Engine**
3. **Fragment Reconstruction Engine**
4. **Forensic Evidence Storage Layer**

---

# 2. Backend Architecture

```
                    ┌─────────────────────────┐
                    │      Client / UI        │
                    │ (Investigator Console)  │
                    └─────────────┬───────────┘
                                  │
                         REST / JSON API
                                  │
                     ┌────────────▼────────────┐
                     │        FastAPI API      │
                     │    (Backend Gateway)    │
                     └───────┬─────────┬───────┘
                             │         │
                    ┌────────▼─┐   ┌───▼─────────┐
                    │  MySQL   │   │ Redis Queue │
                    │ Metadata │   │ Task Broker │
                    └─────┬────┘   └─────┬───────┘
                          │              │
                          │      Async Tasks
                          │              │
                    ┌─────▼──────────────▼─────┐
                    │  AI Processing Engine    │
                    │  PyTorch + IPEX Models   │
                    └───────────┬──────────────┘
                                │
                     ┌──────────▼─────────┐
                     │ Fragment Reassembly │
                     │ Graph Algorithms    │
                     └──────────┬─────────┘
                                │
                        ┌───────▼─────────┐
                        │ Recovered Files │
                        │ Evidence Store  │
                        └─────────────────┘
```

---

# 3. Backend Microservice Components

## 3.1 API Gateway (FastAPI)

Responsible for:

* receiving forensic disk images
* managing recovery tasks
* interacting with AI pipelines
* exposing results to investigators

Core responsibilities:

```
- authentication
- task orchestration
- dataset management
- AI inference requests
- recovery reporting
```

---

## 3.2 AI Processing Engine

Runs the machine learning models described in the technical specification:

Models:

```
1D-CNN with SE blocks
Swin Transformer V2
Entropy classifier
Fragment classification model
```

The engine processes disk fragments in batches.

Processing pipeline:

```
Disk Image
     ↓
Block Scanner
     ↓
Entropy Profiler
     ↓
Fragment Classifier
     ↓
Fragment Storage
```

---

## 3.3 Fragment Reassembly Engine

Responsible for reconstructing files from fragments.

Algorithmic modules:

```
Graph-based fragment sequencing
LSTM semantic adjacency prediction
Genetic optimization search
Coherence of Euclidean Distance metric
```

Output:

```
Reconstructed files
Fragment chains
Confidence scores
```

---

## 3.4 Generative Repair Module

Uses generative models for repairing corrupted data.

Functions:

```
Header reconstruction
Binary inpainting
Corruption repair
Structure restoration
```

Models supported:

```
Diffusion models
GAN based binary repair
Statistical header synthesis
```

---

# 4. Database Design (MySQL)

The backend stores forensic metadata, fragment indexes, AI predictions, and reconstruction results.

## Core Tables

### investigations

```
id
case_name
investigator
description
created_at
```

---

### disk_images

```
id
investigation_id
file_path
size
hash_sha256
upload_time
status
```

---

### fragments

```
id
disk_image_id
offset
block_size
entropy
fragment_hash
classification
confidence
created_at
```

---

### fragment_relationships

```
id
fragment_a
fragment_b
affinity_score
algorithm
```

---

### reconstructed_files

```
id
disk_image_id
file_type
confidence_score
recovered_path
file_size
recovery_status
created_at
```

---

### ai_models

```
id
model_name
model_version
training_dataset
accuracy
created_at
```

---

### forensic_logs

```
id
operation
model_version
parameters
timestamp
investigator
```

These logs ensure **chain-of-custody compliance**.

---

# 5. REST API Specification (FastAPI)

## Upload Disk Image

```
POST /api/upload-image
```

Input

```
multipart/form-data
disk_image
investigation_id
```

Response

```
{
 "image_id": 102,
 "status": "uploaded"
}
```

---

## Start Recovery Process

```
POST /api/recover/{image_id}
```

Response

```
{
 "task_id": "recovery_781",
 "status": "processing"
}
```

---

## Get Fragment Classification

```
GET /api/fragments/{image_id}
```

Response

```
[
 {
  "fragment_id": 12,
  "offset": 8192,
  "entropy": 7.8,
  "file_type": "jpeg",
  "confidence": 0.93
 }
]
```

---

## Get Reconstructed Files

```
GET /api/recovered-files/{image_id}
```

Response

```
[
 {
  "file_type": "pdf",
  "confidence": 0.91,
  "path": "/evidence/recovered/file_32.pdf"
 }
]
```

---

## Download Recovered File

```
GET /api/download/{file_id}
```

---

# 6. Backend Folder Structure

```
ai-file-carving-system
│
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── api
│   │   │   ├── routes_upload.py
│   │   │   ├── routes_recovery.py
│   │   │   ├── routes_results.py
│   │   │
│   │   ├── services
│   │   │   ├── scanner.py
│   │   │   ├── entropy_profiler.py
│   │   │   ├── fragment_classifier.py
│   │   │   ├── reassembly_engine.py
│   │   │   ├── generative_repair.py
│   │   │
│   │   ├── models
│   │   │   ├── cnn_model.py
│   │   │   ├── swin_transformer.py
│   │   │
│   │   ├── database
│   │   │   ├── mysql.py
│   │   │   ├── schemas.py
│   │   │
│   │   ├── workers
│   │   │   ├── celery_worker.py
│
├── docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│
├── models
│
├── datasets
│
└── README.md
```

---

# 7. Docker Deployment

The system must be containerized so that it runs on any machine without dependency conflicts.

## Docker Services

```
fastapi-backend
mysql
redis
celery-worker
```

---

## docker-compose Architecture

```
version: '3.9'

services:

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - mysql
      - redis

  mysql:
    image: mysql:8
    environment:
      MYSQL_DATABASE: forensic_ai
      MYSQL_ROOT_PASSWORD: root
    ports:
      - "3306:3306"

  redis:
    image: redis:7

  worker:
    build: .
    command: celery -A app.workers.celery_worker worker
    depends_on:
      - redis
```

---

# 8. Backend Technology Stack

| Layer            | Technology                  |
| ---------------- | --------------------------- |
| API              | FastAPI                     |
| ML Framework     | PyTorch                     |
| CPU Optimization | Intel Extension for PyTorch |
| Database         | MySQL                       |
| Queue            | Celery                      |
| Broker           | Redis                       |
| Containerization | Docker                      |
| OS               | Linux / Windows WSL         |

---

# 9. Security Requirements

The backend must ensure forensic integrity.

Security measures:

```
SHA256 hashing for evidence files
read-only disk image mounting
audit logging
model version logging
API authentication
```

---

# 10. Performance Requirements

| Metric                  | Target              |
| ----------------------- | ------------------- |
| Disk Scan Speed         | > 500 MB/s          |
| Fragment Classification | < 5 ms per fragment |
| Recovery Rate           | > 90%               |
| Inference Latency       | < 50 ms             |
| CPU Utilization         | > 80%               |

---

# 11. Hardware Requirements

Recommended system:

```
CPU: AMD Ryzen 9 (16+ cores)
RAM: 32GB
Storage: NVMe SSD
GPU: optional
```

Minimum system:

```
CPU: 8 core processor
RAM: 16GB
Storage: SSD
```

---

# 12. Deployment Steps

```
1 Install Docker
2 Clone repository
3 Build containers
4 Start services with docker compose
5 Upload disk images via API
6 Start AI recovery process
7 Download reconstructed files
```

---

# 13. Future Enhancements

```
GPU acceleration with CUDA
Web dashboard
Real-time recovery visualization
Distributed cluster processing
Cloud forensic deployment
```

---

# 14. Final System Deliverables

The completed system includes:

```
FastAPI backend
MySQL forensic database
AI classification pipeline
Fragment reconstruction engine
Dockerized deployment
REST API interface
Forensic logging system
```

---