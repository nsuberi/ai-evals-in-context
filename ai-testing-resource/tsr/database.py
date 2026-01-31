"""SQLAlchemy database models for TSR persistence"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class TSRModel(Base):
    """Test Summary Report database model"""
    __tablename__ = 'test_summary_reports'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    triggered_by = Column(String(100), nullable=False)
    environment = Column(String(50), nullable=False)
    overall_status = Column(String(20), nullable=False)
    go_no_go_decision = Column(String(20), nullable=False)
    decision_reason = Column(Text)
    blocking_issues = Column(JSON, default=[])
    warnings = Column(JSON, default=[])

    # Version manifest
    codebase_sha = Column(String(40), nullable=False)
    codebase_branch = Column(String(255))
    codebase_repo = Column(String(500))
    testbase_sha = Column(String(40), nullable=False)
    prompts_sha = Column(String(40), nullable=False)
    prompts_version = Column(String(50))

    # Approval
    manual_approval_required = Column(Boolean, default=False)
    approved_by = Column(String(255))
    approved_at = Column(DateTime)

    # Relationships
    test_results = relationship("TSRTestResult", back_populates="tsr", cascade="all, delete-orphan")
    eval_iterations = relationship("TSREvalIteration", back_populates="tsr", cascade="all, delete-orphan")
    requirement_coverage = relationship("TSRRequirementCoverage", back_populates="tsr", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TSR {self.id} - {self.go_no_go_decision} - {self.created_at}>"


class TSRTestResult(Base):
    """Test results for a single test type"""
    __tablename__ = 'tsr_test_results'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tsr_id = Column(UUID(as_uuid=True), ForeignKey('test_summary_reports.id'), nullable=False)
    test_type = Column(String(50), nullable=False)
    total = Column(Integer, nullable=False)
    passed = Column(Integer, nullable=False)
    failed = Column(Integer, nullable=False)
    skipped = Column(Integer, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    failure_details = Column(JSON)

    # Relationship
    tsr = relationship("TSRModel", back_populates="test_results")

    def __repr__(self):
        return f"<TSRTestResult {self.test_type} - {self.passed}/{self.total}>"


class TSREvalIteration(Base):
    """Eval iteration summary"""
    __tablename__ = 'tsr_eval_iterations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tsr_id = Column(UUID(as_uuid=True), ForeignKey('test_summary_reports.id'), nullable=False)
    iteration = Column(Integer, nullable=False)
    version_name = Column(String(100), nullable=False)
    prompt_version = Column(String(50))
    outcome = Column(String(20), nullable=False)
    metrics = Column(JSON, nullable=False)
    failure_modes = Column(JSON)
    fixes_applied = Column(JSON)

    # Relationship
    tsr = relationship("TSRModel", back_populates="eval_iterations")

    def __repr__(self):
        return f"<TSREvalIteration {self.version_name} - {self.outcome}>"


class TSRRequirementCoverage(Base):
    """Requirement coverage tracking"""
    __tablename__ = 'tsr_requirement_coverage'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tsr_id = Column(UUID(as_uuid=True), ForeignKey('test_summary_reports.id'), nullable=False)
    requirement_id = Column(String(50), nullable=False)
    requirement_text = Column(Text, nullable=False)
    test_ids = Column(JSON, nullable=False)
    coverage_status = Column(String(20), nullable=False)
    verification_status = Column(String(20), nullable=False)

    # Relationship
    tsr = relationship("TSRModel", back_populates="requirement_coverage")

    def __repr__(self):
        return f"<TSRRequirementCoverage {self.requirement_id} - {self.verification_status}>"


# Database initialization functions
def create_tables(engine):
    """Create all TSR tables in the database

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.create_all(engine)


def drop_tables(engine):
    """Drop all TSR tables from the database

    Args:
        engine: SQLAlchemy engine
    """
    Base.metadata.drop_all(engine)
