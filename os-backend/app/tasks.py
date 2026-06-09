import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurações do Servidor SMTP obtidas via variáveis de ambiente com fallbacks
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "seu_email_gti@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "sua_senha_de_aplicativo")

def enviar_email_protocolo(email_destinatario: str, nome_servidor: str, protocolo: str, descricao: str):
    """Executa o disparo do e-mail de confirmação. Rodará em background."""
    if SMTP_USER == "seu_email_gti@gmail.com":
        print(f"⚠️ SMTP não configurado. Protocolo {protocolo} gerado para {email_destinatario} (Envio pulado).")
        return

    mensagem = MIMEMultipart()
    mensagem["From"] = SMTP_USER
    mensagem["To"] = email_destinatario
    mensagem["Subject"] = f"[GTI ICET] Protocolo de Ordem de Serviço: {protocolo}"

    corpo_email = f"""
    Olá, {nome_servidor},
    
    Sua Ordem de Serviço foi registrada com sucesso na Gerência de TI (GTI/ICET).
    
    DETALHES DO CHAMADO:
    --------------------------------------------------
    Protocolo: {protocolo}
    Descrição do Problema: {descricao}
    Status Inicial: Aberto
    --------------------------------------------------
    
    Você receberá atualizações por este e-mail assim que um técnico assumir o chamado.
    
    Atenciosamente,
    Gerência de TI - ICET/UFAM
    """
    
    mensagem.attach(MIMEText(corpo_email, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Ativa a criptografia TLS
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email_destinatario, mensagem.as_string())
        server.quit()
        print(f"✅ E-mail de protocolo {protocolo} enviado com sucesso para {email_destinatario}!")
    except Exception as e:
        print(f"❌ Falha ao enviar e-mail do protocolo {protocolo}: {e}")