import logging
import sys
from colorama import init, Fore, Style
from .config import settings

# Inicializa o colorama (necessário para Windows)
init(autoreset=True)

class JarvisLogger:
    _instance = None

    def __new__(cls):
        # Padrão Singleton: Garante que só exista um logger no sistema todo
        if cls._instance is None:
            cls._instance = super(JarvisLogger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        self.logger = logging.getLogger("JARVIS_CORE")
        
        # Define o nível baseado no seu config.py
        self.logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        
        # Evita duplicar logs se o logger for chamado novamente
        if self.logger.handlers:
            return

        # --- 1. Handler do Console (Colorido) ---
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # --- 2. Handler do Arquivo (Persistente) ---
        # Usa o LOG_FILE_PATH que definimos no config.py
        try:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            # O encoding='utf-8' é vital para acentos em português
            file_handler = logging.FileHandler(settings.LOG_FILE_PATH, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            # Se falhar ao abrir o arquivo, avisa no console mas não trava o sistema
            print(f"{Fore.RED}Erro crítico ao criar arquivo de log: {e}{Style.RESET_ALL}")

    # --- Métodos de Log Customizados ---

    def debug(self, msg):
        # Só exibe debug se o settings.DEBUG for True
        if settings.DEBUG:
            self.logger.debug(f"{Fore.CYAN}[DEBUG]{Style.RESET_ALL} {msg}")

    def info(self, msg):
        self.logger.info(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

    def warning(self, msg):
        self.logger.warning(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {msg}")

    def error(self, msg):
        self.logger.error(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}")

    def critical(self, msg):
        self.logger.critical(f"{Fore.RED}{Style.BRIGHT}[CRITICAL]{Style.RESET_ALL} {msg}")

# Instância pronta para uso
log = JarvisLogger()