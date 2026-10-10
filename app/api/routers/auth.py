from datetime import datetime, timedelta
import secrets
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.api.schemas import (
    ActionStatusResponse,
    DeleteAccountSchema,
    FamilyInfoResponseSchema,
    FamilyRegisterSchema,
    ForgotPasswordRequestSchema,
    ResetPasswordConfirmSchema,
    TokenResponseSchema,
    UserJoinFamilySchema,
    UserProfileUpdateSchema,
    UserResponseSchema,
)
from app.core.config import settings
from app.domain.models import Author
from app.infrastructure.database import (
    FamilyGroupModel,
    PasswordResetTokenModel,
    UserModel,
    get_db,
)
from app.services.auth_service import AuthService
from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication & Family"])


@router.post("/register-family", response_model=TokenResponseSchema)
def register_family(dto: FamilyRegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.email == dto.first_user_email.strip().lower()).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован")

    family = FamilyGroupModel(id=f"fam-{uuid.uuid4().hex[:8]}", name=dto.family_name.strip())
    db.add(family)

    user = UserModel(
        id=f"usr-{uuid.uuid4().hex[:8]}",
        family_group_id=family.id,
        email=dto.first_user_email.strip().lower(),
        name=dto.first_user_name.strip(),
        hashed_password=AuthService.get_password_hash(dto.first_user_password),
        role=dto.first_user_role.value,
    )
    db.add(user)
    db.commit()

    token = AuthService.create_access_token({"sub": user.id, "fam": family.id})
    return TokenResponseSchema(
        access_token=token,
        user_name=user.name,
        role=Author(user.role),
        family_group_id=family.id,
    )


@router.get("/family-info/{family_group_id}", response_model=FamilyInfoResponseSchema)
def get_family_info(family_group_id: str, db: Session = Depends(get_db)):
    family = db.query(FamilyGroupModel).filter(FamilyGroupModel.id == family_group_id).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Семья с таким кодом не найдена")

    count = db.query(UserModel).filter(UserModel.family_group_id == family_group_id).count()
    return FamilyInfoResponseSchema(id=family.id, name=family.name, members_count=count)


@router.post("/join-family", response_model=TokenResponseSchema)
def join_family(dto: UserJoinFamilySchema, db: Session = Depends(get_db)):
    family = db.query(FamilyGroupModel).filter(FamilyGroupModel.id == dto.family_group_id.strip()).first()
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Семья с указанным ID не найдена")

    clean_email = dto.email.strip().lower()
    if db.query(UserModel).filter(UserModel.email == clean_email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован")

    user = UserModel(
        id=f"usr-{uuid.uuid4().hex[:8]}",
        family_group_id=family.id,
        email=clean_email,
        name=dto.name.strip(),
        hashed_password=AuthService.get_password_hash(dto.password),
        role=dto.role.value,
    )
    db.add(user)
    db.commit()

    token = AuthService.create_access_token({"sub": user.id, "fam": family.id})
    return TokenResponseSchema(
        access_token=token,
        user_name=user.name,
        role=Author(user.role),
        family_group_id=family.id,
    )


@router.post("/login", response_model=TokenResponseSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username.strip().lower()).first()
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный email или пароль")

    token = AuthService.create_access_token({"sub": user.id, "fam": user.family_group_id})
    return TokenResponseSchema(
        access_token=token,
        user_name=user.name,
        role=Author(user.role),
        family_group_id=user.family_group_id,
    )


from sqlalchemy import func


@router.post("/forgot-password", response_model=ActionStatusResponse)
def forgot_password(dto: ForgotPasswordRequestSchema, db: Session = Depends(get_db)):
    clean_email = dto.email.strip().lower()
    user = db.query(UserModel).filter(func.lower(UserModel.email) == clean_email).first()

    if not user:
        return ActionStatusResponse(
            message="Если аккаунт с таким email существует, ссылка для сброса сформирована."
        )

    # Удаляем старые токены сброса
    db.query(PasswordResetTokenModel).filter(PasswordResetTokenModel.user_id == user.id).delete()

    reset_token = secrets.token_urlsafe(32)
    token_entry = PasswordResetTokenModel(
        id=f"rst-{uuid.uuid4().hex[:8]}",
        user_id=user.id,
        token=reset_token,
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    db.add(token_entry)
    db.commit()

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    # 1. Принудительный вывод в консоль Docker
    print("\n" + "=" * 60, flush=True)
    print(f"[СБРОС ПАРОЛЯ] Для: {user.email}", flush=True)
    print(f"ССЫЛКА: {reset_url}", flush=True)
    print("=" * 60 + "\n", flush=True)

    # 2. Если настроен SMTP — отправляем настоящее письмо
    if settings.SMTP_HOST:
        EmailService.send_password_reset_email(user.email, reset_url)
        return ActionStatusResponse(message="Письмо с инструкцией успешно отправлено на вашу почту!")

    # 3. Если SMTP не настроен — отдаем ссылку прямо фронтенду
    return ActionStatusResponse(
        message="Ссылка для смены пароля успешно создана!",
        id=reset_url  # Передаем ссылку во фронтенд
    )


@router.post("/reset-password", response_model=ActionStatusResponse)
def reset_password(dto: ResetPasswordConfirmSchema, db: Session = Depends(get_db)):
    token_entry = db.query(PasswordResetTokenModel).filter(PasswordResetTokenModel.token == dto.token).first()
    if not token_entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недействительная или устаревшая ссылка сброса")

    if token_entry.expires_at < datetime.utcnow():
        db.delete(token_entry)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Срок действия ссылки истек")

    user = db.query(UserModel).filter(UserModel.id == token_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    user.hashed_password = AuthService.get_password_hash(dto.new_password)
    db.delete(token_entry)
    db.commit()

    return ActionStatusResponse(message="Пароль успешно изменён! Теперь вы можете войти.")


@router.get("/me", response_model=UserResponseSchema)
def get_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    return UserResponseSchema(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=Author(current_user.role),
        family_group_id=current_user.family_group_id,
    )


@router.put("/me", response_model=UserResponseSchema)
def update_profile(
    dto: UserProfileUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    user.name = dto.name.strip()
    db.commit()
    db.refresh(user)
    return UserResponseSchema(
        id=user.id,
        name=user.name,
        email=user.email,
        role=Author(user.role),
        family_group_id=user.family_group_id,
    )


@router.delete("/me", response_model=ActionStatusResponse)
def delete_my_account(
    dto: DeleteAccountSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not AuthService.verify_password(dto.password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный пароль")

    family_id = current_user.family_group_id
    user_id = current_user.id

    db.delete(current_user)
    db.commit()

    # Если в семье больше нет других участников, удаляем всю семью каскадно
    remaining_users = db.query(UserModel).filter(UserModel.family_group_id == family_id).count()
    if remaining_users == 0:
        family = db.query(FamilyGroupModel).filter(FamilyGroupModel.id == family_id).first()
        if family:
            db.delete(family)
            db.commit()

    return ActionStatusResponse(message="Аккаунт успешно удалён", id=user_id)