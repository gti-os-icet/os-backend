from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.config import get_db
from app.models import OrdemServico, Gerencia
from app.schemas import OrdemServicoResponse, UpdateStatusDto
from app.auth import check_admin_role

router = APIRouter()

@router.get("/solicitacoes", response_model=List[OrdemServicoResponse])
def listar_todas_solicitacoes(
    status_filtro: Optional[str] = None, 
    db: Session = Depends(get_db), 
    admin_user=Depends(check_admin_role)
):
    """Recupera todas as OS do sistema. Rota restrita e protegida por RBAC."""
    query = db.query(OrdemServico)
    
    # Aplica o filtro de status caso o frontend envie na URL (Ex: ?status_filtro=Aberto)
    if status_filtro:
        query = query.filter(OrdemServico.status == status_filtro)
        
    return query.order_by(OrdemServico.data_solicitacao.desc()).all()

@router.put("/solicitacoes/{id}/status", response_model=OrdemServicoResponse)
def atualizar_status_chamado(
    id: int, 
    update_data: UpdateStatusDto, 
    db: Session = Depends(get_db), 
    admin_user=Depends(check_admin_role)
):
    """Altera o status da OS e vincula o membro da GTI responsável pelo atendimento."""
    # Busca a ordem de serviço informada no parâmetro de rota (Path Parameter)
    os_chamado = db.query(OrdemServico).filter(OrdemServico.id == id).first()
    if not os_chamado:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada.")
        
    # Verifica se o membro da gerência responsável existe
    tecnico = db.query(Gerencia).filter(Gerencia.id == update_data.gerencia_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Membro da equipe GTI não encontrado.")
        
    # Atualiza as informações no objeto
    os_chamado.status = update_data.novo_status
    os_chamado.gerencia_id = update_data.gerencia_id
    
    db.commit()
    db.refresh(os_chamado)
    
    return os_chamado