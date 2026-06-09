import datetime
import random
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.config import get_db
from app.models import OrdemServico, Servidor
from app.schemas import OrdemServicoCreate, OrdemServicoResponse
from app.auth import get_current_user
from app.tasks import enviar_email_protocolo

router = APIRouter()

@router.post("/", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED)
def criar_solicitacao(
    os_data: OrdemServicoCreate, 
    background_tasks: BackgroundTasks, # Injeta o gerenciador de tarefas em segundo plano
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    """Registra uma nova Ordem de Serviço, gera protocolo e dispara e-mail em background."""
    servidor = db.query(Servidor).filter(Servidor.id == os_data.servidor_id).first()
    if not servidor:
        raise HTTPException(status_code=404, detail="Servidor requerente não encontrado.")
    
    ano_atual = datetime.datetime.now().year
    numero_aleatorio = random.randint(1000, 9999)
    protocolo_gerado = f"OS-{ano_atual}-{numero_aleatorio}"
    
    nova_os = OrdemServico(
        protocolo=protocolo_gerado,
        descricao_problema=os_data.descricao_problema,
        status="Aberto",
        servidor_id=os_data.servidor_id
    )
    
    db.add(nova_os)
    db.commit()
    db.refresh(nova_os)
    
    # Adiciona o envio do e-mail na fila do BackgroundTasks (Não trava a resposta HTTP)
    background_tasks.add_task(
        enviar_email_protocolo,
        email_destinatario=servidor.email,
        nome_servidor=servidor.nome,
        protocolo=nova_os.protocolo,
        descricao=nova_os.descricao_problema
    )
    
    return nova_os

@router.get("/historico", response_model=List[OrdemServicoResponse])
def listar_historico_proprio(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Retorna todas as ordens de serviço associadas ao e-mail do usuário logado."""
    servidor = db.query(Servidor).filter(Servidor.email == current_user.email).first()
    if not servidor:
        return []
        
    return db.query(OrdemServico).filter(OrdemServico.servidor_id == servidor.id).all()