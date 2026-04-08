from sqlalchemy import JSON, TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, HardBase, SoftBase, default_uuid


class Report(SoftBase, Base):
    __tablename__ = 'report'
    type = Column(String(), nullable=False)
    severity = Column(Integer(), nullable=False)
    report_case = Column(String(), nullable=False)
    case_number = Column(Integer(), nullable=False)
    title = Column(String(), nullable=False)
    body = Column(String())
    condition = Column(String())
    subscribe_required = Column(Boolean, default=True)
    tags = Column(ARRAY(String()))
    html_sections = relationship('ReportHTMLData')

    checklist = Column(JSON)
    files = relationship('ReportFile')

    # keycloak_groups = relationship('ReportCustomerKeycloak')  # TODO: define ReportCustomerKeycloak model


class ReportFile(Base):
    __tablename__ = 'report_file_tag'
    report_id = Column(ForeignKey('report.id'), primary_key=True)
    file_id = Column(UUID(as_uuid=True), primary_key=True)
    filename = Column(String)
    created_at = Column(TIMESTAMP)
    main_file = Column(Boolean, nullable=False, default=False)


class ThreatCaseFile(Base):
    __tablename__ = 'threat_case_file_tag'
    threat_case_id = Column(UUID(as_uuid=True), primary_key=True)
    file_id = Column(UUID(as_uuid=True), primary_key=True)
    filename = Column(String)


class ReportHTMLData(Base):
    __tablename__ = 'report_html_data'
    id = Column(UUID(as_uuid=True), primary_key=True, default=default_uuid)
    report_id = Column(ForeignKey('report.id'), primary_key=True)
    section = Column(String)
    data = Column(String)
    section_num = Column(Integer, nullable=False)


class ReportAuditLog(Base, HardBase):
    report_id = Column(ForeignKey('report.id'), nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String)
    data = Column(JSONB)
    before = Column(JSONB)
    after = Column(JSONB)
