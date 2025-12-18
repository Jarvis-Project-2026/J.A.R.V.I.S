import webview
import time
import sys
import os

# --- A CLASSE DE API (CÉREBRO) ---
# Métodos aqui podem ser chamados pelo JS via: window.pywebview.api.nome_metodo()
class JarvisAPI:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def start_listening(self):
        print("[PYTHON] 🎤 Microfone ativado...")
        # Simulação de delay de escuta (aqui entraria o SpeechRecognition)
        time.sleep(2)
        return "Comando de voz recebido: 'Iniciar protocolos'"

    def process_command(self, text):
        print(f"[PYTHON] 🧠 Processando: {text}")
        # Simulação de IA (aqui entraria o Gemini/OpenAI)
        time.sleep(1)
        return f"J.A.R.V.I.S: Entendido. Executando ação para '{text}'."

    def shutdown(self):
        print("[PYTHON] 🔌 Encerrando sistemas...")
        if self._window:
            self._window.destroy()

# --- INICIALIZAÇÃO DO SOFTWARE ---
def start_jarvis():
    api = JarvisAPI()
    
    # Define o caminho para o arquivo HTML gerado pelo 'npm run build'
    # Usa caminho absoluto para evitar erros se rodar de outra pasta
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, 'dist', 'index.html')

    # Verifica se o arquivo existe antes de abrir
    if not os.path.exists(html_path):
        print(f"ERRO CRÍTICO: Arquivo não encontrado em: {html_path}")
        print("Você rodou o comando 'npm run build' antes?")
        return

    # Cria a Janela
    window = webview.create_window(
        title='J.A.R.V.I.S. System V1.0',
        url=html_path,     # Carrega o site local
        width=1280,
        height=720,
        frameless=True,    # Sem barra de título (Estilo HUD)
        easy_drag=True,    # Arrastar clicando em qualquer lugar
        on_top=True,       # Opcional: Sempre no topo
        js_api=api         # Conecta o Python ao JavaScript
    )
    
    api.set_window(window)
    
    # Inicia o Loop da Interface
    # debug=True permite abrir o console com F12 (útil para desenvolvimento)
    webview.start(debug=True)

if __name__ == '__main__':
    start_jarvis()