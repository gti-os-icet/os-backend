from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import get_db
from app.models import Gerencia, Servidor
from app.schemas import LoginDto, TokenResponse, UserResponse
from app.auth import verify_password, create_access_token

# ESTA LINHA ESTAVA FALTANDO OU INCORRETA:
router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginDto, db: Session = Depends(get_db)):
    """Rota para autenticar usuários (Gerência ou Servidor) e emitir Token JWT."""
    user = db.query(Gerencia).filter(Gerencia.email == login_data.email).first()
    role = "GTI_Staff"
    
    if not user:
        user = db.query(Servidor).filter(Servidor.email == login_data.email).first()
        role = "Servidor"
        
    if not user or not verify_password(login_data.password, user.password if hasattr(user, 'password') else "senha_mock_invalida"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
    
    access_token = create_access_token(data={"sub": user.email})
    nome_usuario = user.name if hasattr(user, 'name') else user.nome

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            nome=nome_usuario,
            email=user.email,
            role=role
        )
    }