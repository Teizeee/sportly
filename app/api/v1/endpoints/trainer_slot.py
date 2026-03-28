from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.trainer_slot import TrainerSlotAvailability, TrainerSlotCreate, TrainerSlotDayDeleteResult
from app.services.trainer_slot_service import TrainerSlotService

router = APIRouter()

manage_roles = dependencies.require_roles([UserRole.TRAINER, UserRole.GYM_ADMIN])


@router.get(
    "/{trainer_id}/slots",
    response_model=List[TrainerSlotAvailability],
    response_model_exclude_none=False,
    status_code=status.HTTP_200_OK
)
async def get_trainer_slots_by_date(
    trainer_id: str,
    slot_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.get_current_active_user)
):
    trainer_slot_service = TrainerSlotService(db)
    return trainer_slot_service.get_day_slots(trainer_id, slot_date)


@router.post(
    "/{trainer_id}/slots",
    response_model=TrainerSlotAvailability,
    status_code=status.HTTP_201_CREATED
)
async def create_trainer_slot(
    trainer_id: str,
    slot_data: TrainerSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_roles)
):
    trainer_slot_service = TrainerSlotService(db)
    return trainer_slot_service.create_slot(
        current_user=current_user,
        trainer_id=trainer_id,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time
    )


@router.post(
    "/{trainer_id}/slots/day",
    response_model=List[TrainerSlotAvailability],
    response_model_exclude_none=False,
    status_code=status.HTTP_201_CREATED
)
async def create_trainer_slots_for_day(
    trainer_id: str,
    slot_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_roles)
):
    trainer_slot_service = TrainerSlotService(db)
    return trainer_slot_service.create_day_slots(current_user=current_user, trainer_id=trainer_id, slot_date=slot_date)


@router.delete(
    "/{trainer_id}/slots/day",
    response_model=TrainerSlotDayDeleteResult,
    status_code=status.HTTP_200_OK
)
async def delete_trainer_slots_for_day(
    trainer_id: str,
    slot_date: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_roles)
):
    trainer_slot_service = TrainerSlotService(db)
    return trainer_slot_service.delete_day_slots(current_user=current_user, trainer_id=trainer_id, slot_date=slot_date)


@router.delete(
    "/{trainer_id}/slots/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_trainer_slot(
    trainer_id: str,
    slot_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_roles)
):
    trainer_slot_service = TrainerSlotService(db)
    trainer_slot_service.delete_slot(current_user=current_user, trainer_id=trainer_id, slot_id=slot_id)
    return None
