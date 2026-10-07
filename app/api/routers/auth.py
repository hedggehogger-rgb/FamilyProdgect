from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.api.schemas import (
    FamilyRegisterSchema,
    LoginSchema,
    TokenResponseSchema,
    UserJoinFamilySchema,
    UserResponseSchema,
)
from app.domain.models import Author
from app.infrastructure.database import (
    FamilyGroupModel,
    SessionLocal,
    UserModel,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Family"])


@router.post("/register-family", response_model=TokenResponseSchema)
def register_family(dto: FamilyRegisterSchema):
    """Создает новую семью и первого пользователя (например, Мужа)."""
    db: Session = SessionLocal()
    try:
        # Проверяем уникальность email
        if (
            db.query(UserModel)
            .filter(UserModel.email == dto.first_user_email)
            .first()
        ):
            raise HTTPException(
                status_code=400, detail="Email уже зарегистрирован"
            )

        # 1. Создаем семью
        family = FamilyGroupModel(
            id=f"fam-{uuid.uuid4().hex[:8]}",
            name=dto.family_name,
        )
        db.add(family)

        # 2. Создаем первого пользователя
        user = UserModel(
            id=f"usr-{uuid.uuid4().hex[:8]}",
            family_group_id=family.id,
            email=dto.first_user_email,
            name=dto.first_user_name,
            hashed_password=AuthService.get_password_hash(
                dto.first_user_password
            ),
            role=dto.first_user_role.value,
        )
        db.add(user)
        db.commit()

        # 3. Выдаем токен
        token = AuthService.create_access_token(
            {"sub": user.id, "fam": family.id}
        )
        return TokenResponseSchema(
            access_token=token,
            user_name=user.name,
            role=Author(user.role),
            family_group_id=family.id,
        )
    finally:
        db.close()


@router.post("/join-family", response_model=TokenResponseSchema)
def join_family(dto: UserJoinFamilySchema):
    """Регистрирует второго пользователя (например, Жену) в уже существующую семью."""
    db: Session = SessionLocal()
    try:
        # Проверяем, существует ли семья
        family = (
            db.query(FamilyGroupModel)
            .filter(FamilyGroupModel.id == dto.family_group_id)
            .first()
        )
        if not family:
            raise HTTPException(
                status_code=404, detail="Семья с таким ID не найдена"
            )

        if db.query(UserModel).filter(UserModel.email == dto.email).first():
            raise HTTPException(
                status_code=400, detail="Email уже зарегистрирован"
            )

        user = UserModel(
            id=f"usr-{uuid.uuid4().hex[:8]}",
            family_group_id=family.id,
            email=dto.email,
            name=dto.name,
            hashed_password=AuthService.get_password_hash(dto.password),
            role=dto.role.value,
        )
        db.add(user)
        db.commit()

        token = AuthService.create_access_token(
            {"sub": user.id, "fam": family.id}
        )
        return TokenResponseSchema(
            access_token=token,
            user_name=user.name,
            role=Author(user.role),
            family_group_id=family.id,
        )
    finally:
        db.close()


@router.post("/login", response_model=TokenResponseSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Стандартный OAuth2 вход для Swagger и фронтенда."""
    db: Session = SessionLocal()
    try:
        user = (
            db.query(UserModel)
            .filter(UserModel.email == form_data.username)
            .first()
        )
        if not user or not AuthService.verify_password(
            form_data.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный email или пароль",
            )

        token = AuthService.create_access_token(
            {"sub": user.id, "fam": user.family_group_id}
        )
        return TokenResponseSchema(
            access_token=token,
            user_name=user.name,
            role=Author(user.role),
            family_group_id=user.family_group_id,
        )
    finally:
        db.close()


@router.get("/me", response_model=UserResponseSchema)
def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user),
):
    """Возвращает информацию о текущем авторизованном пользователе."""
    return UserResponseSchema(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=Author(current_user.role),
        family_group_id=current_user.family_group_id,
    )