from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import engine, Base
from app.routers import auth, solicitacoes, admin

# Inicializa o FastAPI definindo o título e a documentação automática do projeto
app = FastAPI(
    title="GTI OS ICET - Sistema de Ordem de Serviço",
    description="API RESTful para gerenciamento, triagem e automação de chamados de TI do ICET/UFAM.",
    version="1.0.0",
    docs_url="/docs",        # Link do Swagger UI
    redoc_url="/redoc"       # Interface alternativa de documentação
)

# Configuração do Middleware de CORS (Crucial para permitir que o React do Front acesse a API)
# Durante o desenvolvimento, liberamos para qualquer origem de forma controlada
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que o servidor do React (ex: localhost:5173) faça requisições
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Permite todos os cabeçalhos HTTP necessários
)

# Comando mágico do SQLAlchemy: Lê o models.py e CRIA as tabelas no MySQL se elas não existirem
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Inclusão dos roteadores (Routers) mapeando os prefixos das URLs conforme o contrato da API
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(solicitacoes.router, prefix="/api/v1/solicitacoes", tags=["Solicitações (Servidores)"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Administração (Gerência de TI)"])

# Rota de verificação de integridade (Health Check)
@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "mensagem": "API do Sistema Ordem de Serviço (ICET) operando com sucesso."
    }