from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.progress import ClientProgress
from app.models.user import User
from app.repositories.progress_repository import ProgressRepository
from app.schemas.progress import ClientProgressCreate


class ProgressService:
    def __init__(self, db: Session):
        self.db = db
        self.progress_repo = ProgressRepository(db)

    def create_progress(self, current_user: User, progress_data: ClientProgressCreate) -> ClientProgress:
        self._validate_client_role(current_user)

        bmi = progress_data.bmi or self._calculate_bmi(progress_data.weight, progress_data.height)
        recorded_at = progress_data.recorded_at or datetime.now(timezone.utc)

        return self.progress_repo.create(
            user_id=current_user.id,
            weight=progress_data.weight,
            height=progress_data.height,
            bmi=bmi,
            recorded_at=recorded_at
        )

    def get_my_progress(self, current_user: User) -> List[ClientProgress]:
        self._validate_client_role(current_user)
        return self.progress_repo.get_by_user_id(current_user.id)

    @staticmethod
    def _validate_client_role(current_user: User):
        if current_user.role != "CLIENT":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation is allowed only for CLIENT"
            )

    @staticmethod
    def _calculate_bmi(weight: Decimal, height: Decimal) -> Decimal:
        height_in_meters = height / Decimal("100") if height > Decimal("3") else height
        bmi = weight / (height_in_meters * height_in_meters)
        return bmi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
