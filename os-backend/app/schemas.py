from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ==========================================
# 1. SCHEMAS DE AUTENTICAÇÃO
# ==========================================
class LoginDto(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ==========================================
# 2. SCHEMAS DE SERVIDOR
# ==========================================
class ServidorBase(BaseModel):
    nome: str
    email: EmailStr
    siape: int
    bloco: str
    sala: int

class ServidorCreate(ServidorBase):
    password: str

class ServidorResponse(ServidorBase):
    id: int
    tipo_servidor: str

    class Config:
        from_attributes = True


# ==========================================
# 3. SCHEMAS DE GERÊNCIA
# ==========================================
class GerenciaBase(BaseModel):
    name: str
    email: EmailStr
    cargo: str

class GerenciaCreate(GerenciaBase):
    password: str

class GerenciaResponse(GerenciaBase):
    id: int
    tipo_gerencia: str  # Corrigido o erro de digitação de tipo_genrencia para tipo_gerencia

    class Config:
        from_attributes = True


# ==========================================
# 4. SCHEMAS DE ORDEM DE SERVIÇO (OS)
# ==========================================
class OrdemServicoCreate(BaseModel):
    descricao_problema: str
    servidor_id: int

class UpdateStatusDto(BaseModel):
    novo_status: str
    observacoes_gti: Optional[str] = None
    gerencia_id: int

class OrdemServicoResponse(BaseModel):
    id: int
    protocolo: str
    descricao_problema: str
    status: str
    data_solicitacao: datetime
    servidor_id: int
    gerencia_id: Optional[int] = None
    
    requerente: Optional[ServidorResponse] = None 
    atendente: Optional[GerenciaResponse] = None

    class Config:
        from_attributes = True