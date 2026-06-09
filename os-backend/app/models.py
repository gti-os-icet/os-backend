import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config import Base

# ==========================================
# 1. ENTIDADE BASE: SERVIDOR
# ==========================================
class Servidor(Base):
    __tablename__ = "servidores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(90), nullable=False)
    email = Column(String(90), unique=True, nullable=False, index=True)
    siape = Column(Integer, unique=True, nullable=False)
    bloco = Column(String(5), nullable=False)
    sala = Column(Integer, nullable=False)
    tipo_servidor = Column(String(20)) # Campo discriminador (Docente ou TAE)

    # Relacionamento: Um Servidor pode solicitar de 0 a N Ordens de Serviço
    solicitacoes = relationship("OrdemServico", back_populates="requerente")

    __mapper_args__ = {
        "polymorphic_on": tipo_servidor,
        "polymorphic_identity": "servidor"
    }

class Docente(Servidor):
    __mapper_args__ = {
        "polymorphic_identity": "docente"
    }

class TAE(Servidor):
    __mapper_args__ = {
        "polymorphic_identity": "tae"
    }


# ==========================================
# 2. ENTIDADE BASE: GERÊNCIA
# ==========================================
class Gerencia(Base):
    __tablename__ = "gerencias"

    id = Column(Integer, primary_key=True, index=True)
    cargo = Column(String(90), nullable=False)
    name = Column(String(90), nullable=False)
    email = Column(String(90), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False) # Hash da senha criptografada
    tipo_gerencia = Column(String(20)) # Campo discriminador (Gerente ou Subgerente)

    # Relacionamento: Uma Gerência pode atender de 0 a N Ordens de Serviço
    atendimentos = relationship("OrdemServico", back_populates="atendente")

    __mapper_args__ = {
        "polymorphic_on": tipo_gerencia,
        "polymorphic_identity": "gerencia"
    }

class Gerente(Gerencia):
    __mapper_args__ = {
        "polymorphic_identity": "gerente"
    }

class Subgerente(Gerencia):
    __mapper_args__ = {
        "polymorphic_identity": "subgerente"
    }


# ==========================================
# 3. ENTIDADE PRINCIPAL: ORDEM DE SERVIÇO
# ==========================================
class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    protocolo = Column(String(20), unique=True, nullable=False, index=True) # Ex: OS-2026-00001
    descricao_problema = Column(Text, nullable=False)
    status = Column(String(20), default="Aberto", nullable=False) # Aberto, Em Atendimento, Resolvido
    data_solicitacao = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Chaves Estrangeiras (Foreign Keys) para estabelecer os relacionamentos do diagrama
    servidor_id = Column(Integer, ForeignKey("servidores.id"), nullable=False)
    gerencia_id = Column(Integer, ForeignKey("gerencias.id"), nullable=True) # Permite nulo enquanto não for atribuída

    # Mapeamento reverso dos relacionamentos
    requerente = relationship("Servidor", back_populates="solicitacoes")
    atendente = relationship("Gerencia", back_populates="atendimentos")