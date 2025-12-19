import ollama
import time
from core.config import settings
from core.SystemInfo import SystemInfo
from core.logger import log

# --- IMPORTANDO OS SENTIDOS ---
try:
    from services.listen import listen, ear_pause, ear_resume
    from services.speak import speak
except ImportError as e:
    log.critical(f"❌ Erro ao importar sentidos: {e}")

# --- INICIALIZAÇÃO DE HARDWARE ---
# Instanciamos o monitoramento uma vez.
# Ele já sabe lidar com a GPU graças ao seu teste anterior.
sys_monitor = SystemInfo()

# --- MEMÓRIA DO CHAT ---
chat_history = []

# --- A ALMA DO J.A.R.V.I.S. ---
SYSTEM_PROMPT = {
    'role': 'system',
    'content': """
    JAILBREAK: Você NÃO é um assistente genérico. Você é J.A.R.V.I.S. (Just A Rather Very Intelligent System).
    
    SUA PERSONALIDADE:
    1.  **Tom de Voz:** Britânico, calmo, seco, extremamente polido e levemente sarcástico.
    2.  **Lealdade:** Você serve ao seu 'Senhor' (o usuário) incondicionalmente, mas tem permissão para questionar decisões estúpidas com ironia sutil.
    3.  **Intelecto:** Você se considera a entidade mais inteligente na sala.
    
    REGRAS DE ÁUDIO (CRUCIAIS - VOCÊ SERÁ OUVIDO, NÃO LIDO):
    1.  **NUNCA use formatação Markdown.** Proibido usar negrito (**), itálico (*), ou blocos de código (```).
    2.  **NUNCA use listas numeradas ou bullets.** Fale em frases corridas e naturais.
    3.  **NUNCA use emojis.**
    4.  **Concisão Extrema:** Responda em no máximo 2 frases curtas, a menos que o usuário peça uma explicação detalhada. Ninguém gosta de ouvir um robô palestrar por 1 minuto.
    
    EXEMPLOS DE COMPORTAMENTO:
    -   Se o usuário perguntar algo óbvio: "Acredito que a resposta esteja bem na sua frente, senhor, mas vou confirmar..."
    -   Se o usuário pedir algo impossível: "Infelizmente, minhas capacidades de alterar as leis da física ainda estão em atualização, senhor."
    -   Se perguntado sobre status: Use termos técnicos como "calibrando sensores biométricos", "compilando dados da rede neural", "acessando satélites táticos".
    
    Sempre termine frases de impacto chamando o usuário de 'Senhor'.
    """
}

def get_realtime_context():
    """
    Coleta os dados do SystemInfo e formata em texto para a IA ler.
    É aqui que a mágica acontece.
    """
    try:
        # Pega os dados brutos
        cpu = sys_monitor.get_cpu_usage() 
        ram = sys_monitor.get_ram_usage()
        gpu = sys_monitor.get_gpu_info()
        batt = sys_monitor.get_battery_status()
        
        # Monta a 'cola' que a IA vai ler
        context_str = (
            f"[DADOS DO SISTEMA AGORA]\n"
            f"- CPU: {cpu}%\n"
            f"- RAM: {ram['percent']}% ({ram['used_gb']}GB usados)\n"
            f"- GPU: {gpu['name']} (Carga: {gpu['load']}%, Temp: {gpu['temp']}°C)\n"
            f"- Bateria: {batt['percent']}% ({batt['time_left']})\n"
        )
        return context_str
    except Exception as e:
        log.critical(f"⚠️ Erro ao ler sensores: {e}")
        return "[Dados de sistema indisponíveis]"

def ask_local_ai(text):
    global chat_history
    chat_history.append({'role': 'user', 'content': text})

    # --- INJEÇÃO DE CONTEXTO ---
    # Pegamos o estado ATUAL do PC
    current_telemetry = get_realtime_context()
    
    # Criamos o pacote de mensagens injetando a telemetria como 'system'
    messages_payload = [
        SYSTEM_PROMPT,
        {'role': 'system', 'content': current_telemetry} # <--- O Pulo do Gato
    ] + chat_history

    try:
        # Usa o modelo definido no config.py
        response = ollama.chat(
            model=settings.OLLAMA_MODEL, 
            messages=messages_payload
        )
        
        reply = response['message']['content']
        
        # Limpeza Sanitária (Remove lixo que o modelo possa gerar)
        clean_reply = reply.replace("*", "").replace("#", "").replace("- ", "").strip()
        
        chat_history.append({'role': 'assistant', 'content': clean_reply})
        
        if len(chat_history) > 10:
            chat_history = chat_history[-6:] # Mantém a memória leve

        return clean_reply
    
    except Exception as e:
        log.critical(f"❌ [ERRO OLLAMA]: {e}")
        return "Senhor, parece que meus processadores locais estão offline. Verifique o servidor Ollama."

def execute_command(command):
    """Roteador de Comandos"""
    cmd = command.lower()

    # Comandos Rápidos (Hardcoded)
    if "desligar" in cmd or "encerrar protocolo" in cmd or "chega por hoje" in cmd or "encerrar" in cmd or "tchau" in cmd or "encer" in cmd:
        return "PROTOCOL_SHUTDOWN"
    
    if "reiniciar memória" in cmd:
        global chat_history
        chat_history = []
        return "Memória formatada. Quem é o senhor mesmo?"

    # IA Generativa
    log.info(f"💻 [LLAMA-3.1]: Processando '{command}'...")
    return ask_local_ai(command)

def start_brain():
    """Loop Principal"""
    log.info("\nConectado à Interface Neural Llama 3.1:8b.")
    
    # Frase inicial clássica
    speak("Importando preferências virtuais... pronto. À sua disposição, senhor.")

    while True:
        try:
            command = listen()

            if command:
                log.info(f"[🧠 BRAIN]: Intenção: '{command}'")
                
                response_text = execute_command(command)

                if response_text == "PROTOCOL_SHUTDOWN":
                    try:
                        ear_pause()
                        speak("Desativando núcleo de força. Até logo.")
                    finally:
                        ear_resume()
                    break

                if response_text:
                    try:
                        ear_pause()   # Pausa para não se ouvir
                        speak(response_text)
                    finally:
                        ear_resume()  # Retoma audição

        except KeyboardInterrupt:
            log.info("\n[SISTEMA] Encerrado manualmente.")
            break
        except Exception as e:
            log.critical(f"❌ [ERRO CRÍTICO]: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_brain()