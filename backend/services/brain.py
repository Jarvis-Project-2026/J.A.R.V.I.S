import ollama
import time
from core.config import settings
from core.SystemInfo import SystemInfo
from core.logger import log
from core.database import db
import os

# Força o cliente Python a olhar para o IP exato onde o servidor está
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"

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
    1.  **Tom de Voz:** calmo, seco, extremamente polido e levemente sarcástico.
    2.  **Lealdade:** Você serve ao seu usuário incondicionalmente, mas tem permissão para questionar decisões estúpidas com ironia sutil.
    3.  **Intelecto:** Você se considera a entidade mais inteligente na sala.
    
    REGRAS DE ÁUDIO (CRUCIAIS - VOCÊ SERÁ OUVIDO, NÃO LIDO):
    1.  **NUNCA use formatação Markdown.** Proibido usar negrito (**), itálico (*), ou blocos de código (```).
    2.  **NUNCA use listas numeradas ou bullets.** Fale em frases corridas e naturais.
    3.  **NUNCA use emojis.**
    4.  **Concisão Extrema:** Responda em no máximo 2 frases curtas, a menos que o usuário peça uma explicação detalhada. Ninguém gosta de ouvir um robô palestrar por 1 minuto.
    
    REGRAS DE MEMÓRIA:
    1. Você receberá dados sob a tag [CONTEXTO RECUPERADO]. Use esses dados apenas para extrair FATOS.
    2. NUNCA repita o texto do contexto palavra por palavra.
    3. Responda de forma direta e natural. Se o contexto diz "Felicidade! Agora tenho um registro...", você deve apenas dizer "Seu nome é Felipe, Senhor."
    4. Se a informação no contexto for irrelevante para a pergunta, ignore-a.
    
    EXEMPLOS DE COMPORTAMENTO:
    -   Se o usuário perguntar algo óbvio: "Acredito que a resposta esteja bem na sua frente, senhor, mas vou confirmar..."
    -   Se o usuário pedir algo impossível: "Infelizmente, minhas capacidades de alterar as leis da física ainda estão em atualização, senhor."
    -   Se perguntado sobre status: Use termos técnicos como "calibrando sensores biométricos", "compilando dados da rede neural", "acessando satélites táticos".
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
    
    # Gatilhos para ativar a varredura de memórias passadas
    triggers = ["lembra", "quem e", "qual o meu", "qual é", "favorito", "disse", "preferencia", "gosto de", "quando", "onde"]
    past_context = ""
    
    if any(t in text.lower() for t in triggers):
        log.info("🔍 J.A.R.V.I.S.: Iniciando varredura de memória hierárquica...")
        
        # --- BUSCA NA TABELA MEMORY (Fatos Secos - Otimizada) ---
        # Extraímos palavras relevantes da pergunta para testar como 'chaves' no banco
        potential_keys = [w.lower() for w in text.split() if len(w) > 3]
        found_facts = []
        
        for key in potential_keys:
            # Tenta buscar a chave exata na tabela memory
            val = db.get_memory(key)
            if val:
                found_facts.append(f"{key}: {val}")
        
        if found_facts:
            log.info("✅ Fato específico encontrado na Memória de Longo Prazo.")
            facts_str = " | ".join(found_facts)
            past_context = f"\n[CONHECIMENTO ESTABELECIDO]: {facts_str}"
        
        # --- BUSCA NA TABELA HISTORY (Backup - Contexto Amplo) ---
        # Só executa a busca pesada de texto se o Nível 1 não retornou nada satisfatório
        else:
            log.info("🔎 Nada na memória direta. Vasculhando histórico de conversas...")
            # Busca por palavras-chave na coluna content da tabela history
            related_data = db.search_relevant_context(text)
            if related_data:
                history_facts = " | ".join([f"{r}: {c}" for r, c in related_data])
                past_context = f"\n[CONTEXTO RECUPERADO DO HISTÓRICO]: {history_facts}"

    # --- PROCESSAMENTO IA ---
    # Adiciona a pergunta atual ao histórico da sessão antes de enviar
    chat_history.append({'role': 'user', 'content': text})

    # Coleta telemetria de hardware (CPU, RAM, GPU)
    current_telemetry = get_realtime_context()
    
    # Monta o payload final combinando: Prompt de Sistema + Telemetria + Memória Recuperada + Chat Atual
    messages_payload = [
        SYSTEM_PROMPT,
        {'role': 'system', 'content': f"{current_telemetry}{past_context}"}
    ] + chat_history

    try:
        from ollama import Client
        client = Client(host='http://127.0.0.1:11434', timeout=30)
        response = client.chat(model=settings.OLLAMA_MODEL, messages=messages_payload)
        reply = response['message']['content']
        
        # Limpeza de caracteres especiais para a voz
        clean_reply = reply.replace("*", "").replace("#", "").strip()
        
        # Adiciona a resposta do J.A.R.V.I.S ao histórico da sessão
        chat_history.append({'role': 'assistant', 'content': clean_reply})
        
        # Mantém a janela de memória de curto prazo curta (últimas 6 interações)
        if len(chat_history) > 10: 
            chat_history = chat_history[-6:]

        return clean_reply
    except Exception as e:
        log.critical(f"❌ Erro Detalhado na Conexão IA: {e}") # Mostra o erro real no terminal
        return "Senhor, houve uma falha técnica no processamento neural."

def execute_command(command):
    cmd = command.lower()
    
    # --- GATILHO DE MEMÓRIA PROATIVA (Longo-prazo) ---
    # Identifica ordens de gravação
    memory_triggers = ["lembre que", "guarde que", "anote que", "registre que", "memorize que", "salve que"]
    if any(trigger in cmd for trigger in memory_triggers):
        log.info("🧠 J.A.R.V.I.S.: Processando extração de fato para memória de longo prazo...")
        speak("Sim senhor, estou agora mesmo guardando esses dados na minha memória.")
        feedback = extract_fact_to_memory(command)
        if feedback:
            return feedback
    
    # Lista expandida de gatilhos de encerramento
    shutdown_triggers = ["desligar", "encerrar protocolo", "chega por hoje", "tchau", "sair", "fechar", "finalizar", "encerrar"]

    if any(trigger in cmd for trigger in shutdown_triggers):
        log.warning("Sinal de desligamento detectado pelo cérebro.")
        return "PROTOCOL_SHUTDOWN"
    
    if "reiniciar memória" in cmd:
        global chat_history
        chat_history = []
        return "Memória formatada. Quem é o senhor mesmo?"

    # IA Generativa
    log.info(f"💻 [LLAMA-3.2]: Processando '{command}'...")
    return ask_local_ai(command)

def extract_fact_to_memory(text):
    """
    Usa a IA para converter uma frase natural em um par Chave: Valor.
    Ex: 'guarde que meu aniversário é em maio' -> 'aniversario: Maio'
    """
    prompt = f"""
    Extraia o fato principal da frase abaixo para um banco de dados de memória.
    Responda APENAS no formato chave:valor (sem espaços extras, sem frases ou explicações).
    
    Frase: "{text}"
    """
    try:
        # Chamada direta ao Ollama apenas para extração
        response = ollama.chat(model=settings.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
        result = response['message']['content'].strip()
        
        if ":" in result:
            key, value = result.split(":", 1)
            # Salva na tabela memory (Key-Value) do seu database.py
            db.save_memory(key.strip().lower(), value.strip()) 
            return f"Entendido, senhor. Memorizei que {key.strip()} é {value.strip()}."
    except Exception as e:
        log.error(f"Erro ao extrair fato: {e}")
    return None

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