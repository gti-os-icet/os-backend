from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.config import get_db
from app.models import Gerencia, Servidor
from app.schemas import TokenResponse, UserResponse
from app.auth import verify_password, create_access_token

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(
    login_data: OAuth2PasswordRequestForm = Depends(), # Captura os dados no padrão do Swagger/OAuth2
    db: Session = Depends(get_db)
):
    """Rota para autenticar usuários (Gerência ou Servidor) e emitir Token JWT."""
    
    # login_data.username conterá o e-mail inserido no formulário
    user = db.query(Gerencia).filter(Gerencia.email == login_data.username).first()
    role = "GTI_Staff"
    
    if not user:
        user = db.query(Servidor).filter(Servidor.email == login_data.username).first()
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