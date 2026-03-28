from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class ClientProgress(Base):
    __tablename__ = "client_progress"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    weight = Column(DECIMAL(5, 2), nullable=False)
    height = Column(DECIMAL(5, 2), nullable=False)
    bmi = Column(DECIMAL(5, 2), nullable=False)
    recorded_at = Column(DateTime, nullable=False)

    user = relationship("User", uselist=False)

    def __repr__(self):
        return f"<ClientProgress {self.id} user={self.user_id} bmi={self.bmi}>"
