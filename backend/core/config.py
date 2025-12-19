import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 1. Definição de Caminhos Absolutos
# O arquivo atual é backend/core/config.py
# .parent = backend/core/
# .parent.parent = backend/
FILE_PATH = Path(__file__).resolve()
BACKEND_DIR = FILE_PATH.parent.parent
ROOT_DIR = BACKEND_DIR.parent  # A raiz do projeto (onde fica o .env)

# 2. Carregar variáveis de ambiente (.env)
env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    # --- Informações do Projeto ---
    PROJECT_NAME: str = "J.A.R.V.I.S."
    VERSION: str = "1.0.0"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    DEBUG: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"

    # --- Caminhos de Diretórios (Essencial para não dar erro de file not found) ---
    DIR_ROOT = ROOT_DIR
    DIR_BACKEND = BACKEND_DIR
    DIR_LOGS = BACKEND_DIR / "logs"
    LOG_FILE_PATH = DIR_LOGS / "jarvis.log"
    DIR_DATABASE = BACKEND_DIR / "database"
    DIR_SOUNDS = BACKEND_DIR / "assets" / "sounds"
    
    # --- Configurações de IA Local (Ollama) ---
    # Agora o modelo é controlado por aqui. Se mudar no .env, muda no cérebro todo.
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # Adicionado: Timeouts Globais (Robustez de Rede)
    TIMEOUT_API: int = 10  # Segundos para esperar a IA responder
    TIMEOUT_VOICE: int = 5 # Segundos para esperar o reconhecimento de voz

    # --- Configurações de Áudio (Listen/Speak) ---
    DEFAULT_LANGUAGE: str = "pt-BR"
    SPEECH_RATE: int = int(os.getenv("SPEECH_RATE", 200))    # Velocidade da fala
    MIC_INDEX: int = int(os.getenv("MIC_INDEX", 0)) # Índice do microfone padrão

    # --- Configurações do Banco de Dados ---
    DB_NAME: str = "jarvis_memory.db"
    DB_PATH = DIR_DATABASE / DB_NAME

    def create_dirs(self):
        """Garante que a infraestrutura de pastas exista."""
        self.DIR_LOGS.mkdir(parents=True, exist_ok=True)
        self.DIR_DATABASE.mkdir(parents=True, exist_ok=True)
        self.DIR_SOUNDS.mkdir(parents=True, exist_ok=True)

    def perform_sanity_check(self):
        """
        Verificação de Saúde do Sistema (Modo Local).
        """
        # Verifica se as pastas cruciais foram criadas
        if not self.DIR_BACKEND.exists():
            print(f"❌ ERRO FATAL: Pasta backend não encontrada em {self.DIR_BACKEND}")
            sys.exit(1)

        # Aviso de Modo Debug
        if self.DEBUG:
            print(f"⚠️  AVISO: Modo DEBUG ativado. O sistema será mais verboso.")

        # Aviso Informativo sobre o Modelo
        print(f"🧠 Modelo de IA definido: {self.OLLAMA_MODEL} (Local)")

# Instância única
settings = Settings()
settings.create_dirs()
settings.perform_sanity_check()