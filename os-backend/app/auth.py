import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import get_db
from app.models import Gerencia, Servidor

# Configurações de Segurança
SECRET_KEY = os.getenv("SECRET_KEY", "SUA_CHAVE_SECRETA_SUPER_PROTEGIDA_DO_ICET_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Contexto para Hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de extração do token Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de acesso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Gerencia).filter(Gerencia.email == email).first()
    if user:
        return user

    user = db.query(Servidor).filter(Servidor.email == email).first()
    if user:
        return user

    raise credentials_exception

# ESTA FUNÇÃO PRECISA ESTAR AQUI:
def check_admin_role(current_user=Depends(get_current_user)):
    if not hasattr(current_user, 'tipo_gerencia') or current_user.tipo_gerencia is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Esta rota é restrita à Gerência de TI."
        )
    return current_user