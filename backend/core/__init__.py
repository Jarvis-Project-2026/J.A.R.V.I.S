import logging
from .config import settings

# --- 1. Filtro de Poluição (Noise Reduction) ---
# Silencia bibliotecas que "falam demais" no console
LIBRARIES_TO_SILENCE = [
    "urllib3", 
    "asyncio", 
    "multipart", 
    "httpcore",
    "httpx" # Ollama usa muito isso
]

for lib in LIBRARIES_TO_SILENCE:
    logging.getLogger(lib).setLevel(logging.WARNING)

# --- 2. Exports ---
# Comentei o SystemInfo por enquanto para não dar erro se o arquivo não existir.
# Assim que criar o SystemInfo.py, pode descomentar.
# from .SystemInfo import SystemInfo 

__all__ = ["settings"] 
# __all__ = ["settings", "SystemInfo"]