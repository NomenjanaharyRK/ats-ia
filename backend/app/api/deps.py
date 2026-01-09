from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import crud
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User

# ✅ UTILISE VOS NOMS DE VARIABLES
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.model_config.get('env_file', '.env').split('/')[-1]}/auth/login"  # Simple
    # OU directement
    # tokenUrl="/api/v1/auth/login"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET,  # ✅ VOTRE variable
            algorithms=[settings.JWT_ALGORITHM]  # ✅ VOTRE variable
        )
        token_data = payload if isinstance(payload, dict) else {}
        user_id: str = token_data.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Impossible de valider les identifiants",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les identifiants",
        )
    
    user = crud.user.get(db, id=int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user
