import webview
import time
import sys
import os
import threading

# Importa as configurações, o Logger e agora a Memória (Database)
from core.config import settings
from core.logger import log 
from core.database import db

# --- IMPORTAÇÃO DOS MÓDULOS ---
try:
    log.debug("Carregando serviços cognitivos (Audição, Fala, Cérebro)...")
    from services.listen import listen, ear_pause, ear_resume
    from services.speak import speak
    from services.brain import execute_command
    log.info("Serviços cognitivos carregados com sucesso.")
except ImportError as e:
    log.critical(f"Falha na importação dos módulos de serviço: {e}")
    sys.exit(1)

is_running = True
window_instance = None

def update_ui(status, message):
    """Envia comando para o Frontend mudar o visual"""
    global window_instance
    if window_instance and is_running:
        safe_msg = message.replace("'", "").replace('"', "")
        try:
            window_instance.evaluate_js(f"window.receiveStatus('{status}', '{safe_msg}')")
        except Exception as e:
            log.error(f"Falha ao atualizar UI (Bridge Python-JS): {e}")

# --- CICLO DE VIDA DO JARVIS ---
def jarvis_auto_loop():
    global is_running, window_instance
    
    time.sleep(2) 
    log.info(f"Interface Gráfica Conectada. Loop principal ativo.")
    
    # Exemplo de uso da memória: Recuperar nome do usuário se existir
    user_name = db.get_memory("user_name") or "Senhor"
    msg_boas_vindas = f"Sistemas sincronizados. Bem-vindo de volta, {user_name}."
    
    update_ui("SPEAKING", msg_boas_vindas)
    speak(msg_boas_vindas)
    
    while is_running:
        try:
            log.debug("Estado: Ouvindo...")
            update_ui("LISTENING", "Aguardando comando...")
            
            command = listen()

            if command and is_running:
                # SALVAR NO HISTÓRICO (Entrada do Usuário)
                db.log_interaction("user", command)
                
                log.info(f"Comando recebido: '{command}'")
                update_ui("PROCESSING", f"Processando: {command}")
                
                response_text = execute_command(command)

                # Protocolo de desligamento
                if response_text == "PROTOCOL_SHUTDOWN":
                    log.warning("Protocolo de desligamento iniciado.")
                    is_running = False
                    break

                if response_text:
                    # SALVAR NO HISTÓRICO (Resposta do JARVIS)
                    db.log_interaction("assistant", response_text)
                    
                    log.info(f"Resposta: '{response_text}'")
                    update_ui("SPEAKING", response_text)
                    
                    try:
                        ear_pause()
                        speak(response_text)
                    finally:
                        ear_resume()
                        
        except Exception as e:
            log.error(f"Erro no loop principal: {e}")
            time.sleep(1)
    
    log.info("Loop principal encerrado.")

# --- API JS <-> PYTHON ---
class JarvisAPI:
    def __init__(self): self._window = None
    def set_window(self, window): self._window = window
    def shutdown(self):
        global is_running
        log.warning("Shutdown via UI")
        is_running = False
        if self._window: self._window.destroy()

# --- INICIALIZAÇÃO ---
def start_jarvis():
    global window_instance
    log.info(f"Inicializando {settings.PROJECT_NAME} v{settings.VERSION}")
    
    api = JarvisAPI()
    html_path = str(settings.DIR_ROOT / 'frontend' / 'dist' / 'index.html')

    if not os.path.exists(html_path):
        log.critical(f"Frontend não encontrado em: {html_path}")
        window_instance = webview.create_window('Erro', html='<h1>Erro Crítico: Frontend não encontrado</h1>')
        
    else:
        window_instance = webview.create_window(
            title=settings.PROJECT_NAME,
            url=html_path,
            width=1920,
            height=1080,
            frameless=True,
            js_api=api,
            resizable=True,
            transparent=False,
            background_color='#000000'
        )

    api.set_window(window_instance)
    t = threading.Thread(target=jarvis_auto_loop, daemon=True)
    t.start()

    webview.start(debug=settings.DEBUG)

if __name__ == '__main__':
    start_jarvis()