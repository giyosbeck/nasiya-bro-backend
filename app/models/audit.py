from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(64), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    actor = relationship("User", foreign_keys=[actor_user_id])
    target = relationship("User", foreign_keys=[target_user_id])
