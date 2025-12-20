import asyncio
import edge_tts
import pygame
import os
import pyttsx3
import re
import sys
import time
import threading
import uuid
from core.config import settings
from core.logger import log
from colorama import init, Fore, Style

# --- CONFIGURAÇÕES ---
VOICE_ONLINE = "pt-BR-AntonioNeural"
# Removemos a variável global fixa AUDIO_FILE pois agora será dinâmica

# Inicializa o motor offline (Backup)
engine_offline = pyttsx3.init()
engine_offline.setProperty('rate', settings.SPEECH_RATE)

# Inicializa o mixer do Pygame (Apenas uma vez)
try:
    pygame.mixer.init()
except:
    log.critical("Erro ao iniciar sistema de áudio.")

# --- EFEITOS VISUAIS (CINEMÁTICA) ---
def typewriter_effect(text, level="INFO"):
    """
    Simula a digitação mantendo o padrão de cores e prefixo do logger.
    """
    # Preparamos o prefixo baseado no nível (seguindo seu padrão no logger.py)
    prefix = f"{Fore.GREEN}[INFO]{Style.RESET_ALL}"
    if level == "WARN": prefix = f"{Fore.YELLOW}[WARN]{Style.RESET_ALL}"
    
    # Formata o cabeçalho do log manualmente para o efeito
    timestamp = time.strftime('%H:%M:%S')
    header = f"{timestamp} | {level} | {prefix} "
    
    sys.stdout.write(header)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.04)
    sys.stdout.write('\n') # Quebra de linha apenas no final da fala

# --- TRATAMENTO DE TEXTO ---
def _treat_text(text):
    SLANG_MAP = {
        r"\bvc\b": "você",
        r"\btmj\b": "tamo junto",
        r"\bpq\b": "porque",
        r"\badd\b": "adicionar",
        r"\bmsg\b": "mensagem",
        r"\bobs\b": "observação",
    }
    text = re.sub(r'[^\w\s,.?!áéíóúàãõâêôçÁÉÍÓÚÀÃÕÂÊÔÇ]', '', text)
    for slang, expansion in SLANG_MAP.items():
        text = re.sub(slang, expansion, text, flags=re.IGNORECASE)
    return text.strip()

# --- ONLINE ---
async def _generate_audio_online(text, file_path):
    # ACEITA O file_path COMO ARGUMENTO AGORA
    clean_text = _treat_text(text)
    communicate = edge_tts.Communicate(clean_text, VOICE_ONLINE, rate="+10%")
    await communicate.save(file_path)

def speak_online(text):
    # GERA UM NOME ÚNICO PARA CADA FALA
    # Isso evita o erro de "Arquivo em uso" no Windows
    filename_path = settings.DIR_SOUNDS / f"audio_{uuid.uuid4().hex}.mp3"
    filename_str = str(filename_path)
    
    try:
        # Passamos o filename gerado para a função
        asyncio.run(_generate_audio_online(text, filename_str))

        pygame.mixer.music.load(filename_str)
        pygame.mixer.music.play()

        visual_thread = threading.Thread(target=typewriter_effect, args=(f"[J.A.R.V.I.S]: {text}",))
        visual_thread.start()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        visual_thread.join()
        
        pygame.mixer.music.unload() # Libera o arquivo do Windows
        
        # Agora é seguro deletar
        if os.path.exists(filename_str):
            os.remove(filename_str)
        return True

    except Exception as e:
        log.info(f"[AVISO] Falha na voz online: {e}")
        # Tenta limpar o lixo caso tenha dado erro
        if os.path.exists(filename_str):
            try: os.remove(filename_str)
            except: pass
        return False 

# --- OFFLINE ---
def speak_offline(text):
    log.info("[MODO OFFLINE] Ativando voz de backup...")
    typewriter_effect(f"[J.A.R.V.I.S]: {text}")
    
    clean_text = _treat_text(text)
    engine_offline.say(clean_text)
    engine_offline.runAndWait()

# --- MAIN ---
def speak(text):
    if not speak_online(text):
        speak_offline(text)

if __name__ == "__main__":
    speak("Protocolo de correção de áudio aplicado. Nomes de arquivos agora são dinâmicos.")