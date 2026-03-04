from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class InvestigationBase(BaseModel):
    case_name: str
    investigator: Optional[str] = None
    description: Optional[str] = None


class InvestigationCreate(InvestigationBase):
    pass


class Investigation(InvestigationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DiskImageBase(BaseModel):
    investigation_id: int
    file_path: str
    size: Optional[int] = None
    hash_sha256: Optional[str] = None
    status: str = "uploaded"


class DiskImageCreate(DiskImageBase):
    pass


class DiskImage(DiskImageBase):
    id: int
    upload_time: datetime

    class Config:
        from_attributes = True


class FragmentBase(BaseModel):
    disk_image_id: int
    offset: int
    block_size: int
    entropy: Optional[float] = None
    fragment_hash: Optional[str] = None
    classification: Optional[str] = None
    confidence: Optional[float] = None


class Fragment(FragmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReconstructedFileBase(BaseModel):
    disk_image_id: int
    file_type: str
    confidence_score: Optional[float] = None
    recovered_path: str
    file_size: Optional[int] = None
    recovery_status: str


class ReconstructedFile(ReconstructedFileBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
