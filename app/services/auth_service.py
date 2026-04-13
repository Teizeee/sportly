from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.service import ClientMembership, UserTrainerPackage
from app.repositories.client_membership_repository import ClientMembershipRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_trainer_package_repository import UserTrainerPackageRepository
from app.schemas.user import (
    ActiveClientMembership,
    ActiveUserTrainerPackage,
    GetUserTrainerWithPassword,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserBlock,
    PasswordChange,
    UsersCount,
)
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.client_membership_repo = ClientMembershipRepository(db)
        self.user_trainer_package_repo = UserTrainerPackageRepository(db)

    def register(self, current_user: User, user_data: UserCreate, subsystem: str) -> User:
        normalized_subsystem = subsystem.lower()
        if normalized_subsystem not in {"web", "mobile"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Некорректный заголовок Subsystem. Допустимые значения: "web" или "mobile"'
            )

        if normalized_subsystem == "web" and user_data.role == UserRole.CLIENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Регистрация клиента из подсистемы web запрещена"
            )

        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        if user_data.role == "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не может самостоятельно зарегистрироваться как SUPER_ADMIN"
            )
        if user_data.role == "TRAINER":
            if current_user is not None and current_user.role == "GYM_ADMIN":
                user_data.gym_id = current_user.gym.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Пользователь может быть зарегистрирован как TRAINER только администратором зала"
                )
            

        hashed_password = get_password_hash(user_data.password)
        user = self.user_repo.create(user_data, hashed_password)

        return user

    def login(self, login_data: UserLogin, subsystem: str) -> dict:
        user = self.user_repo.get_by_email(login_data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Аккаунт удален"
            )

        if user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Аккаунт заблокирован. Причина: {user.blocked_comment or 'Причина не указана'}"
            )

        if not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        normalized_subsystem = subsystem.lower()
        if normalized_subsystem not in {"web", "mobile"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Некорректный заголовок Subsystem. Допустимые значения: "web" или "mobile"'
            )

        if normalized_subsystem == "web" and user.role not in {UserRole.SUPER_ADMIN, UserRole.GYM_ADMIN}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вход через web разрешен только для SUPER_ADMIN и GYM_ADMIN"
            )

        if normalized_subsystem == "mobile" and user.role not in {UserRole.CLIENT, UserRole.TRAINER}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вход через mobile разрешен только для CLIENT и TRAINER"
            )

        access_token = create_access_token(
            subject=user.id,
            role=user.role.value
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role.value
        }

    def get_current_user(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Аккаунт удален"
            )

        return user
    
    def get_users(
        self,
        current_user: User,
        gym_id: Optional[str],
        role: Optional[UserRole],
        include_blocked: Optional[bool]
    ) -> List[GetUserTrainerWithPassword]:
        if current_user.role == "GYM_ADMIN":
            if current_user.gym.id != gym_id or role in ["GYM_ADMIN", "SUPER_ADMIN"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав"
                )

        users = self.user_repo.get_all(
            gym_id, role, include_blocked
        )

        active_membership_by_user_id: Dict[str, ClientMembership] = {}
        active_package_by_user_id: Dict[str, UserTrainerPackage] = {}
        if gym_id and role == UserRole.CLIENT and users:
            user_ids = [user.id for user in users]
            active_membership_by_user_id = self.client_membership_repo.get_active_by_user_ids_for_gym(
                user_ids=user_ids,
                gym_id=gym_id
            )
            active_package_by_user_id = self.user_trainer_package_repo.get_active_by_user_ids_for_gym(
                user_ids=user_ids,
                gym_id=gym_id
            )

        return [
            self._serialize_user_for_user_list(
                current_user=current_user,
                user=user,
                gym_id=gym_id,
                role=role,
                include_blocked=include_blocked,
                active_membership=active_membership_by_user_id.get(user.id),
                active_package=active_package_by_user_id.get(user.id)
            )
            for user in users
        ]
    
    def users_count(self) -> UsersCount:
        stats = self.user_repo.get_count()
        return UsersCount(
            total=stats.total,
            clients=stats.clients,
            trainers=stats.trainers,
            gym_admins=stats.gym_admins
        )

    def update_profile(self, user_id: str, update_data: UserUpdate) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if update_data.email is not None:
            existing_user = self.user_repo.get_by_email(update_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Электронная почта уже используется"
                )

        return self.user_repo.update(user, update_data)

    def update_user_by_admin(self, current_user: User, target_user_id: str, update_data: UserUpdate) -> User:
        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if current_user.role == UserRole.GYM_ADMIN:
            if (
                target_user.role != UserRole.TRAINER or
                not target_user.trainer_profile or
                not current_user.gym or
                target_user.trainer_profile.gym_id != current_user.gym.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав"
                )

        return self.update_profile(target_user_id, update_data)

    def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        user = self.get_current_user(user_id)

        if not verify_password(password_data.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Текущий пароль неверный"
            )

        hashed_password = get_password_hash(password_data.new_password)
        self.user_repo.update_password(user, hashed_password, password_data.new_password)

        return True

    def block_user(self, admin_id: str, target_user_id: str, block_data: UserBlock) -> User:
        if admin_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя заблокировать супер-админа"
            )

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return self.user_repo.block(target_user, block_data)

    def unblock_user(self, admin_id: str, target_user_id: str) -> User:
        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        return self.user_repo.unblock(target_user)

    def delete_user(self, user_id: str, target_user_id: str) -> bool:
        current_user = self.get_current_user(user_id)

        if user_id == target_user_id and current_user.role == "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя удалить супер-админа"
            )

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        if current_user.role == "GYM_ADMIN" and target_user.role == "TRAINER" and target_user.trainer_profile.gym_id == current_user.gym.id:
            self.user_repo.delete(target_user)
            return True

        if user_id != target_user_id and current_user.role != "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для удаления других пользователей"
            )

        self.user_repo.delete(target_user)
        return True

    @staticmethod
    def _get_user_gym_blocked_at(user: User, gym_id: str):
        for gym_blocking in user.gym_blockings:
            if gym_blocking.gym_id == gym_id:
                return gym_blocking.created_at
        return None

    @staticmethod
    def _to_active_membership_model(
        membership: Optional[ClientMembership]
    ) -> Optional[ActiveClientMembership]:
        if membership is None:
            return None
        return ActiveClientMembership(
            id=membership.id,
            user_id=membership.user_id,
            membership_type_id=membership.membership_type_id,
            membership_type_name=membership.membership_type.name,
            status=membership.status,
            purchased_at=membership.purchased_at,
            activated_at=membership.activated_at,
            expires_at=membership.expires_at
        )

    @staticmethod
    def _to_active_package_model(
        package: Optional[UserTrainerPackage]
    ) -> Optional[ActiveUserTrainerPackage]:
        if package is None:
            return None
        trainer_user = package.trainer_package.trainer.user
        return ActiveUserTrainerPackage(
            id=package.id,
            user_id=package.user_id,
            trainer_package_id=package.trainer_package_id,
            trainer_package_name=package.trainer_package.name,
            trainer_package_session_count=package.trainer_package.session_count,
            trainer_first_name=trainer_user.first_name,
            trainer_last_name=trainer_user.last_name,
            trainer_patronymic=trainer_user.patronymic,
            status=package.status,
            sessions_left=package.sessions_left,
            purchased_at=package.purchased_at,
            activated_at=package.activated_at
        )

    def _serialize_user_for_user_list(
        self,
        current_user: User,
        user: User,
        gym_id: Optional[str],
        role: Optional[UserRole],
        include_blocked: Optional[bool],
        active_membership: Optional[ClientMembership] = None,
        active_package: Optional[UserTrainerPackage] = None
    ) -> GetUserTrainerWithPassword:
        serialized = GetUserTrainerWithPassword.model_validate(user, from_attributes=True)

        if serialized.trainer_profile and not self._can_view_trainer_password(current_user, user):
            serialized.trainer_profile.password = None

        if gym_id and role == UserRole.CLIENT and include_blocked is True:
            serialized.blocked_at = self._get_user_gym_blocked_at(user, gym_id)

        if gym_id and role == UserRole.CLIENT:
            serialized.active_membership = self._to_active_membership_model(active_membership)
            serialized.active_package = self._to_active_package_model(active_package)

        return serialized

    def _can_view_trainer_password(self, current_user: User, target_user: User) -> bool:
        if target_user.role != UserRole.TRAINER or not target_user.trainer_profile:
            return False

        if current_user.role == UserRole.SUPER_ADMIN:
            return True

        if current_user.role == UserRole.GYM_ADMIN and current_user.gym:
            return target_user.trainer_profile.gym_id == current_user.gym.id

        return False
