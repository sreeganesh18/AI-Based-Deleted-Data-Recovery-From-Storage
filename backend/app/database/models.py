from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class Investigation(Base):
    __tablename__ = "investigations"
    id = Column(Integer, primary_key=True, index=True)
    case_name = Column(String(255), nullable=False)
    investigator = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    disk_images = relationship(
        "DiskImage", back_populates="investigation", cascade="all, delete"
    )


class DiskImage(Base):
    __tablename__ = "disk_images"
    id = Column(Integer, primary_key=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"))
    file_path = Column(String(512), nullable=False)
    size = Column(Integer)
    hash_sha256 = Column(String(64))
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="uploaded")

    investigation = relationship("Investigation", back_populates="disk_images")
    fragments = relationship(
        "Fragment", back_populates="disk_image", cascade="all, delete"
    )
    reconstructed_files = relationship(
        "ReconstructedFile", back_populates="disk_image", cascade="all, delete"
    )


class Fragment(Base):
    __tablename__ = "fragments"
    id = Column(Integer, primary_key=True, index=True)
    disk_image_id = Column(Integer, ForeignKey("disk_images.id"))
    offset = Column(Integer)
    block_size = Column(Integer)
    entropy = Column(Float)
    fragment_hash = Column(String(64))
    classification = Column(String(50))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    disk_image = relationship("DiskImage", back_populates="fragments")


class FragmentRelationship(Base):
    __tablename__ = "fragment_relationships"
    id = Column(Integer, primary_key=True, index=True)
    fragment_a = Column(Integer, ForeignKey("fragments.id"))
    fragment_b = Column(Integer, ForeignKey("fragments.id"))
    affinity_score = Column(Float)
    algorithm = Column(String(100))


class ReconstructedFile(Base):
    __tablename__ = "reconstructed_files"
    id = Column(Integer, primary_key=True, index=True)
    disk_image_id = Column(Integer, ForeignKey("disk_images.id"))
    file_type = Column(String(50))
    confidence_score = Column(Float)
    recovered_path = Column(String(512))
    file_size = Column(Integer)
    recovery_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    disk_image = relationship("DiskImage", back_populates="reconstructed_files")


class AIModel(Base):
    __tablename__ = "ai_models"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255))
    model_version = Column(String(50))
    training_dataset = Column(String(255))
    accuracy = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ForensicLog(Base):
    __tablename__ = "forensic_logs"
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(255))
    model_version = Column(String(50))
    parameters = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    investigator = Column(String(255))
