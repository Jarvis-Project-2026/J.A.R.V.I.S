import webview
import time
import sys
import os
import threading

# Importa as configurações, o Logger e agora a Memória (Database)
from core.config import settings
from core.logger import log 
from core.database import db
from core.bridge import JarvisAPI

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
    global window_instance
    if window_instance and is_running:
        clean_msg = message.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
        script = f"if(window.receiveStatus) {{ window.receiveStatus('{status}', '{clean_msg}'); }}"
        try:
            window_instance.evaluate_js(script)
        except Exception as e:
            log.error(f"Erro na Bridge: {e}")

# --- CICLO DE VIDA DO JARVIS ---
def jarvis_auto_loop():
    global is_running, window_instance
    
    time.sleep(4) 
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

                if response_text == "PROTOCOL_SHUTDOWN":
                    log.warning("Iniciando sequência de encerramento total.")
                    update_ui("PROCESSING", "Desconectando...")
                    
                    try:
                        ear_pause()
                        speak("Desativando núcleo de força. Até logo, Senhor.")
                    finally:
                        is_running = False
                        if window_instance:
                            window_instance.destroy() # Fecha a interface gráfica
                        
                        log.info("Aplicação encerrada com sucesso.")
                        os._exit(0) # Mata todos os processos e threads imediatamente
                        break

                if response_text:
                    # SALVAR NO HISTÓRICO (Resposta do JARVIS)
                    db.log_interaction("assistant", response_text)
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
window_instance = None
api = JarvisAPI()

# --- INICIALIZAÇÃO ---
def start_jarvis():
    global window_instance, api
    settings.perform_sanity_check()
    log.info(f"Inicializando {settings.PROJECT_NAME} v{settings.VERSION}")
    html_path = str(settings.DIR_ROOT / 'frontend' / 'dist' / 'index.html')

    if not os.path.exists(html_path):
        log.critical(f"Frontend não encontrado em: {html_path}")
        window_instance = webview.create_window('Erro', html='<h1>Erro Crítico: Frontend não encontrado</h1>')
        return
        
    window_instance = webview.create_window(
        title=settings.PROJECT_NAME,
        url=html_path,
        js_api=api,
        fullscreen=True,
        frameless=True,
        background_color='#000000',
        easy_drag=True,
        
    )

    api.set_window(window_instance)
    t = threading.Thread(target=jarvis_auto_loop, daemon=True)
    t.start()

    webview.start(debug=settings.DEBUG)

if __name__ == '__main__':
    try:
        start_jarvis()
    except KeyboardInterrupt:
        log.info("Aplicação finalizada pelo usuário.")
        import os
        os._exit(0)