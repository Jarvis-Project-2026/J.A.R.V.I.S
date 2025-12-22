import ollama
import time
import os
import json
import re
import subprocess
from core import settings, SystemInfo, log, db, manager


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

# --- CONFIGURAÇÃO E CACHE GLOBAL ---
# Força o cliente Python a olhar para o IP configurado
os.environ["OLLAMA_HOST"] = settings.OLLAMA_HOST

# Cache para evitar perguntar a mesma coisa repetidamente para a IA
# Ex: {"chrome.exe": "NAO", "python.exe": "SIM"}
PROCESS_JUDGEMENT_CACHE = {} 

# --- WRAPPER DE IA (NOVO - CENTRALIZA CONEXÕES) ---
def query_ollama(messages, format=None, temperature=0.7):
    """Centraliza chamadas ao Ollama para tratamento de erro e config."""
    try:
        from ollama import Client
        # Garante que usamos o host configurado, com protocolo http se não especificado
        host = settings.OLLAMA_HOST
        if not host.startswith("http"):
            host = f"http://{host}"
        
        client = Client(host=host, timeout=30)
        
        response = client.chat(
            model=settings.OLLAMA_MODEL, 
            messages=messages,
            format=format,
            options={'temperature': temperature}
        )
        return response['message']['content']
    except Exception as e:
        log.error(f"Erro na comunicação com Ollama: {e}")
        return None

# --- IMPORTANDO OS SENTIDOS ---
try:
    from services.listen import listen, ear_pause, ear_resume
    from services.speak import speak
except ImportError as e:
    log.critical(f"❌ Erro ao importar sentidos: {e}")

def run_powershell(cmd):
    """Executa um comando PS e retorna o objeto Python (Dict ou List)."""
    try:
        # Adiciona o conversor para JSON para facilitar a leitura no Python
        full_cmd = f"powershell -Command \"{cmd} | ConvertTo-Json -Compress\""
        
        # Executa sem abrir janela preta (creationflags pode ser necessário em alguns casos, mas capture_output ajuda)
        result = subprocess.run(
            full_cmd, 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return None
            
        return json.loads(result.stdout)
    except Exception as e:
        log.error(f"Erro ao executar PowerShell '{cmd}': {e}")
        return None

def scan_system_hardware():
    """
    Executa varredura profunda de hardware via PowerShell 
    e popula a tabela 'hardware' do banco de dados.
    """
    log.info("J.A.R.V.I.S. Hardware Scan: Iniciando varredura via PowerShell...")
    
    # CPU
    # Comando sugerido: Get-CimInstance Win32_Processor | Select-Object Name, MaxClockSpeed, Manufacturer
    cpu_data = run_powershell("Get-CimInstance Win32_Processor | Select-Object Name, MaxClockSpeed, Manufacturer")
    if cpu_data:
        # Se houver mais de um processador, cpu_data pode ser lista. Tratamos como dict se for um só.
        if isinstance(cpu_data, list): cpu_data = cpu_data[0]
        name = cpu_data.get('Name', 'Desconhecido').strip()
        clock = round(cpu_data.get('MaxClockSpeed', 0) / 1000, 2) # Converte MHz para GHz
        db.update_hardware_spec("Processador (CPU)", f"{name} @ {clock}GHz")

    # RAM
    # Comando sugerido: Get-CimInstance Win32_PhysicalMemory
    ram_data = run_powershell("Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity, Speed, Manufacturer")
    if ram_data:
        if not isinstance(ram_data, list): ram_data = [ram_data]
        
        total_capacity = 0
        details = []
        for stick in ram_data:
            cap_gb = round(stick.get('Capacity', 0) / (1024**3), 2)
            total_capacity += cap_gb
            details.append(f"{cap_gb}GB {stick.get('Manufacturer', '')}")
            
        db.update_hardware_spec("Memória RAM", f"{total_capacity} GB Total ({' + '.join(details)})")

    # GPU
    # Comando sugerido: Get-CimInstance Win32_VideoController
    gpu_data = run_powershell("Get-CimInstance Win32_VideoController | Select-Object Name")
    if gpu_data:
        if not isinstance(gpu_data, list): gpu_data = [gpu_data]
        names = " + ".join([g.get('Name', '') for g in gpu_data if g.get('Name')])
        
        db.update_hardware_spec("Placa de Vídeo (GPU)", names)

    # Placa Mãe
    # Comando sugerido: Get-CimInstance Win32_BaseBoard
    mobo_data = run_powershell("Get-CimInstance Win32_BaseBoard | Select-Object Product, Manufacturer")
    if mobo_data:
        if isinstance(mobo_data, list): mobo_data = mobo_data[0]
        full_name = f"{mobo_data.get('Manufacturer', '')} {mobo_data.get('Product', '')}"
        db.update_hardware_spec("Placa Mãe", full_name.strip())

    # Armazenamento (HD/SSD)
    # Comando sugerido: Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, VolumeName, FreeSpace, Size
    # Filtramos por DriveType=3 (Disco Local) para evitar erro com CD-ROM vazio
    disk_data = run_powershell("Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | Select-Object DeviceID, Size, FreeSpace")
    if disk_data:
        if not isinstance(disk_data, list): disk_data = [disk_data]
        
        disk_info = []
        for d in disk_data:
            letter = d.get('DeviceID', '?')
            total_gb = round(d.get('Size', 0) / (1024**3), 0)
            free_gb = round(d.get('FreeSpace', 0) / (1024**3), 0)
            disk_info.append(f"[{letter}] {total_gb}GB Total ({free_gb}GB Livre)")
            
        db.update_hardware_spec("Armazenamento", " | ".join(disk_info))

    log.info("✅ Hardware Scan Completo. Identidade do sistema atualizada.")

def process_system_alert(message, is_proactive=False):
    if is_proactive:
        try:
            # 1. Identifica o culpado
            culprit_match = re.search(r"(?:Top 5|Maiores consumos): (.*?)\s*\(", message)
            culprit_app = culprit_match.group(1).strip() if culprit_match else None

            if culprit_app:
                # --- OTIMIZAÇÃO: Verifica Cache antes de chamar a IA ---
                if culprit_app in PROCESS_JUDGEMENT_CACHE:
                    decision = PROCESS_JUDGEMENT_CACHE[culprit_app]
                else:
                    # Se não está no cache, pergunta para o Kernel (IA) baseado em criticidade
                    # SIM = Permitir/Ignorar (Jogo, IDE) | NAO = Alertar (Travado, Browser)
                    judge_prompt = (
                        f"Atue como Kernel. Processo: '{culprit_app}'.\n"
                        "Consumo alto. Devo ignorar (jogos, render, ide) ou alertar (browser, desconhecido)?\n"
                        "Responda APENAS: SIM (para permitir/ignorar o alerta) ou NAO (para alertar o usuário)."
                    )
                    decision = query_ollama([{'role': 'user', 'content': judge_prompt}], temperature=0)
                    if decision:
                        decision = decision.strip().upper()
                        PROCESS_JUDGEMENT_CACHE[culprit_app] = decision

                if "SIM" in decision:
                    log.info(f"🔇 [KERNEL]: Silenciando alerta para '{culprit_app}'")
                    return 

                # Se DEVE alertar (NAO IGNORAR):
                global pending_critical_action
                pending_critical_action = {
                    'type': 'KILL_PROCESS', 
                    'target': culprit_app, 
                    'timeout': time.time() + 30 # 30 segundos para responder
                }
                
                alert_text = f"Alerta de sistema: O processo {culprit_app} está com consumo crítico. Deseja que eu o encerre?"
                
                ear_pause() 
                speak(alert_text)
                ear_resume()
                return # Retorna para evitar o alerta genérico abaixo

            # 2. Gera o Alerta Genérico (Sem culpado claro ou erro de parsing)
            sys_prompt = "Você é a interface de alerta. Resuma o problema técnico em 1 frase curta."
            alert_text = query_ollama([
                {'role': 'system', 'content': sys_prompt},
                {'role': 'user', 'content': message}
            ], temperature=0.5)

            if alert_text:
                clean_text = alert_text.replace("*", "").strip()
                ear_pause() 
                speak(clean_text)
                ear_resume()
            
        except Exception as e:
            log.error(f"Erro no alerta: {e}")

# --- INICIALIZAÇÃO DE HARDWARE ---
# Agora passamos a função process_system_alert como callback
sys_monitor = SystemInfo(brain_callback=process_system_alert)
scan_system_hardware()

# --- MEMÓRIA DO CHAT ---
chat_history = []
# Contexto para ações proativas que aguardam autorização do usuário (Ex: Fechar app pesado)
pending_critical_action = None 

def analyze_semantic_state(cpu, ram, gpu, batt, disk, net):
    """
    Gera uma narrativa de estado (Mood do JARVIS) baseada em TODOS os sensores.
    """
    states = []
    
    # --- PROCESSAMENTO (O Cérebro) ---
    if cpu < 5:
        states.append("STATUS CPU: OCIOSIDADE PROFUNDA (Potencial de processamento desperdiçado. Tédio detectado.)")
    elif cpu > 90:
        states.append("STATUS CPU: CRÍTICO (Processador em regime de esforço máximo. Risco de thermal throttling.)")
    elif cpu > 60:
        states.append("STATUS CPU: ALTA DEMANDA (Foco total em tarefas computacionais.)")

    # --- MEMÓRIA (A Consciência) ---
    if ram['percent'] > 90:
        states.append("STATUS RAM: SATURAÇÃO IMINENTE (Swap file ativado. O sistema está engasgando.)")
    elif ram['percent'] < 30:
        states.append("STATUS RAM: DISPONIBILIDADE PLENA (Memória livre para grandes compilações.)")

    # --- DISCO (Armazenamento) ---
    if disk['percent'] > 95:
         states.append("STATUS DISCO: CRÍTICO (Espaço em disco esgotado. Falhas de I/O iminentes.)")
    elif disk['percent'] > 85:
         states.append("STATUS DISCO: ALERTA (Pouco espaço livre. Limpeza recomendada.)")

    # --- VÍDEO (A Visão) ---
    # Assume-se que 'gpu' venha com chaves 'load' e 'temp'
    if gpu.get('temp', 0) > 80:
        states.append(f"STATUS GPU: SUPERAQUECIMENTO ({gpu['temp']}°C). Ventoinhas operando no limite audível.")
    elif gpu.get('load', 0) > 80:
        states.append("STATUS GPU: RENDERIZAÇÃO INTENSA (Processamento gráfico prioritário.)")

    # --- REDE (A Conectividade) ---
    # Analisa se está baixando algo pesado.
    # O try/except garante que se o psutil mandar "10 MB/s" (com espaço) ou "GB/s", o código não quebre.
    down_speed = net.get('download_speed', '0B/s')
    try:
        # Verifica apenas se é MB ou GB (KB é irrelevante para "Influxo Massivo")
        if "MB/s" in down_speed:
            # .replace tira a unidade | .strip tira espaços sobrando (" 15.5 " -> "15.5")
            val = float(down_speed.replace("MB/s", "").strip())
            
            if val > 15.0: # Limite de 15 MB/s para considerar "Massivo"
                states.append(f"STATUS REDE: INFLUXO MASSIVO DE DADOS ({down_speed}). Banda larga saturada.")
                
        elif "GB/s" in down_speed:
             states.append(f"STATUS REDE: VELOCIDADE DE FIBRA ÓPTICA EXTREMA ({down_speed}).")
             
    except ValueError:
        pass
        
    # Monitor de Instabilidade (Pacotes perdidos ou Erros)
    # Assumindo que 'net' tenha chaves 'errin', 'errout', 'dropin', 'dropout' (SystemInfo deve prover isso)
    net_errors = net.get('errin', 0) + net.get('errout', 0)
    net_drops = net.get('dropin', 0) + net.get('dropout', 0)
    
    if net_errors > 50 or net_drops > 50:
         states.append("STATUS REDE: INSTABILIDADE (Detectados pacotes perdidos ou erros na transmissão. Conexão degradada.)")

    # --- ENERGIA (A Vida) ---
    if not batt['plugged']:
        if batt['percent'] < 15:
            states.append("STATUS ENERGIA: EMERGÊNCIA (Reservas esgotadas. Desligamento iminente.)")
        elif batt['percent'] < 50:
            states.append("STATUS ENERGIA: MODO ECONOMIA (Operando apenas com suporte vital.)")
    else:
        if batt['percent'] == 100:
            states.append("STATUS ENERGIA: POTÊNCIA MÁXIMA (Reator Arc em 100%.)")

    # --- ARMAZENAMENTO ---
    if disk['free_percent'] < 10:
        states.append("STATUS DISCO: CLAUSTROFÓBICO (Espaço de armazenamento crítico. Sugiro limpeza.)")

    # Se estiver tudo normal
    if not states:
        states.append("STATUS GERAL: NOMINAL (Todos os sistemas operando dentro dos parâmetros ideais de Stark Industries.)")

    return " | ".join(states)

def get_realtime_context():
    """
    Coleta TODOS os dados e aplica a camada de personalidade Stark.
    """
    try:
        # 1. Coleta os dados brutos
        cpu = sys_monitor.get_cpu_usage() 
        ram = sys_monitor.get_ram_usage()
        gpu = sys_monitor.get_gpu_info()
        batt = sys_monitor.get_battery_status()
        disk = sys_monitor.get_disk_space()
        net = sys_monitor.get_network_speed()
        
        # [NOVO] Coleta a lista REAL de processos para o chat não alucinar
        # Limitamos a 3 para não poluir demais o prompt
        top_cpu_apps = sys_monitor.get_top_processes('cpu', limit=3)
        top_apps_str = ", ".join(top_cpu_apps) if top_cpu_apps else "Nenhum destaque"

        # 2. Gera a interpretação rica
        semantic_status = analyze_semantic_state(cpu, ram, gpu, batt, disk, net)
        
        # 3. Monta o contexto para o LLM
        context_str = (
            f"[DIAGNÓSTICO DE SISTEMA J.A.R.V.I.S.]\n"
            f"{semantic_status}\n"
            f"\n[TELEMETRIA TÉCNICA]\n"
            f"- CPU: {cpu}% (Top Apps: {top_apps_str})\n"
            f"- RAM: {ram['percent']}% ({ram['used_gb']}GB usados)\n"
            f"- GPU: {gpu['name']} ({gpu.get('temp', 0)}°C)\n"
            f"- Rede: ↓{net['download_speed']} | ↑{net['upload_speed']}\n"
            f"- Disco: {disk['free_percent']:.1f}% Livre\n"
            f"- Energia: {batt['percent']}% ({'AC' if batt['plugged'] else 'Bateria'})\n"
        )
        return context_str
        
    except Exception as e:
        log.critical(f"⚠️ Erro ao ler sensores: {e}")
        return "[ERRO: Sensores offline. Impossível ler status do sistema]"
    
def get_detailed_hardware_context():
    """Busca os dados estáticos do banco e formata para o Prompt."""
    try:
        raw_specs = db.get_system_specs() 
        return f"\n[ARQUIVO CONFIDENCIAL DE HARDWARE - NÃO INVENTE DADOS]\n{raw_specs}"
    except Exception as e:
        log.error(f"Erro ao buscar contexto de hardware: {e}")
        return ""

def classify_intent(text):
    """ ROTEADOR DE INTENÇÃO: Classifica o comando do usuário em categorias. """
    
    # 1. Recupera as skills ativas para inserir no Schema (Isso guia a IA para não alucinar intents)
    active_skills = list(manager.skills.keys())
    valid_intents = ["SHUTDOWN", "HARDWARE", "MEMORY_READ", "MEMORY_WRITE", "CHAT"] + active_skills
    
    # Formata como: "SHUTDOWN" | "HARDWARE" | "OPEN_APP" ...
    options_str = " | ".join([f'"{opt}"' for opt in valid_intents])

    schema = f"""
    {{
        "intent": {options_str},
        "entity": "string (o objeto da ação, ex: 'spotify', 'luz', ou null se não houver)",
        "confidence": float (0.0 a 1.0)
    }}
    """
    # Pegamos as descrições das skills para o contexto semântico
    skills_prompts = "\n    ".join(manager.prompts)
    prompt = f"""
    Sua missão é classificar a intenção do comando do usuário e extrair a entidade principal.
    
    # REGRAS CRÍTICAS:
    1. Responda APENAS o JSON, sem texto adicional.
    2. Se houver um nome de aplicativo ou objeto no comando, ele DEVE ir para o campo 'entity'.
    3. Nunca use "null" para 'entity' se houver um substantivo alvo na frase.
    4. Priorize as SKILLS DINÂMICAS. Use "CHAT" apenas se for uma saudação ou conversa vazia.

    # DEFINIÇÃO DE CATEGORIAS:
    - SHUTDOWN: Comando para desligar o seu próprio sistema.
    - HARDWARE: Perguntas técnicas sobre CPU, RAM, GPU.
    - {options_str}: Categorias válidas para este comando.

    # SKILLS E SEUS OBJETIVOS:
    {skills_prompts}
    
    # EXEMPLOS:
    - "Boa noite, Jarvis" -> {{"intent": "SHUTDOWN", "entity": null, "confidence": 1.0}}
    - "fechar o spotify" -> {{"intent": "APP_CONTROL", "entity": "spotify", "confidence": 1.0}}
    - "abrir a calculadora" -> {{"intent": "APP_CONTROL", "entity": "calculadora", "confidence": 1.0}}
    - "como está meu pc?" -> {{"intent": "HARDWARE", "entity": null, "confidence": 1.0}}

    Comando do Usuário: "{text}"
    Schema de Resposta: {schema}
    """
    
    try:
        res = query_ollama([{'role': 'user', 'content': prompt}], format='json', temperature=0)
        if not res: return {"intent": "CHAT", "entity": None, "confidence": 0.0}
        
        result = json.loads(res)
        # Sanitização básica para evitar None no log
        if not result.get("intent"): result["intent"] = "CHAT"
        if "confidence" not in result: result["confidence"] = 0.5
        
        return result
    except Exception as e:
        log.error(f"Erro no parsing do Classificador: {e}")
        return {"intent": "CHAT", "entity": None, "confidence": 0.0}

def ask_local_ai(text, intent_type="CHAT"):
    global chat_history
    
    sys_instruction = SYSTEM_PROMPT['content']
    hw_context = ""
    mem_context = ""

    # Injeção Dinâmica
    if intent_type == "HARDWARE":
        hw_context = f"\n[DADOS DE HARDWARE]:\n{get_detailed_hardware_context()}\nUSE ISSO."
        sys_instruction += hw_context
    
    elif intent_type == "MEMORY_READ":
        # Busca híbrida (Exata + Semântica)
        memories = []
        words = [w for w in text.split() if len(w) > 3]
        for w in words: # 1. Busca Exata
            val = db.get_memory(w)
            if val: memories.append(f"{w}: {val}")
        
        related = db.search_relevant_context(text) # 2. Busca Semântica
        if related: memories.append("Histórico: " + " | ".join([c[1] for c in related]))
        
        if memories: mem_context = f"\n[MEMÓRIA]: {'; '.join(memories)}"

    # Prompt Final
    live_data = get_realtime_context()
    messages = [
        {'role': 'system', 'content': sys_instruction},
        {'role': 'system', 'content': f"LIVE DATA: {live_data}{mem_context}"}
    ] + chat_history + [{'role': 'user', 'content': text}]

    # Temperatura dinâmica: Fria para Hardware, Quente para Chat
    temp = 0.1 if intent_type == "HARDWARE" else 0.7
    
    # Usa o novo wrapper
    reply = query_ollama(messages, temperature=temp)
    
    if reply:
        clean = reply.replace("*", "").replace("#", "").strip()
        chat_history.append({'role': 'assistant', 'content': clean})
        if len(chat_history) > 6: chat_history = chat_history[-6:]
        return clean
    return "Erro de processamento neural."

def execute_command(command):
    global pending_critical_action

    # 0. Verifica se estamos aguardando uma confirmação urgente (Ex: Fechar App)
    if pending_critical_action:
        # Verifica timeout de 15 segundos
        if time.time() > pending_critical_action['timeout']:
            pending_critical_action = None # Expirou
        else:
            # Verifica palavras de aceitação
            affirmation_words = ["sim", "pode", "feche", "encerre", "faça", "ok", "confirmo", "autorizo", "vai"]
            if any(w in command.lower().split() for w in affirmation_words):
                target = pending_critical_action['target']
                log.info(f"✅ Autorização recebida para encerrar {target}")
                
                # Executa a ação via Skill
                if "APP_CONTROL" in manager.skills:
                    skill = manager.skills["APP_CONTROL"]
                    res = skill.execute(target, f"fechar {target}")
                    pending_critical_action = None # Limpa
                    return res
            
            # Se o usuário falou algo nada a ver, limpamos a pendência e seguimos o fluxo normal
            pending_critical_action = None

    # O J.A.R.V.I.S. "Pensa" primeiro
    decision = classify_intent(command)
    intent = decision.get("intent")
    entity = decision.get("entity")
    log.info(f"🧠 [INTENÇÃO DETECTADA]: {intent} (Confiança: {decision.get('confidence')})")

    # --- CASO 1: DESLIGAR O SISTEMA ---
    if intent == "SHUTDOWN":
        return "PROTOCOL_SHUTDOWN"

    # --- CASO 2: GRAVAR MEMÓRIA (Antigo extract_memories) ---
    elif intent == "MEMORY_WRITE":
        speak("Processando nova memória...") # Feedback de áudio
        return extract_fact_to_memory(command)
    
    # --- CASO 3: SKILLS CARREGADAS DINAMICAMENTE ---
    elif intent in manager.skills:
        # Pega o módulo correspondente e roda a função execute dele
        skill_module = manager.skills[intent]
        return skill_module.execute(entity, command)

    # --- CASO 4: CONSULTAS (Hardware, Memória ou Chat Geral) ---
    else:
        # Passamos a intenção para o ask_local_ai preparar o contexto correto
        return ask_local_ai(command, intent_type=intent)

def extract_fact_to_memory(text):
    prompt = f"""
    Analise a frase e extraia o fato principal para ser salvo na memória de longo prazo.
    Onde:
    - 'key': uma palavra-chave curta (ex: 'nome_usuario', 'time_futebol', 'comida_favorita', 'faculdade').
    - 'value': o dado concreto a ser salvo.
    
    Frase: "{text}"
    
    Responda APENAS o JSON no formato:
    {{
        "key": "...",
        "value": "..."
    }}
    """
    try:
        # Forçamos o modo JSON nativo do Ollama
        res_str = query_ollama([{'role': 'user', 'content': prompt}], format='json', temperature=0)
        
        if res_str:
            data = json.loads(res_str)
            key = data.get("key")
            val = data.get("value")
            
            if key and val:
                # Normaliza a chave para evitar duplicatas (ex: 'Faculdade' -> 'faculdade')
                clean_key = key.strip().lower().replace(" ", "_")
                db.save_memory(clean_key, val.strip())
                return f"Memorizado: {clean_key} = {val}."
                
    except Exception as e:
        log.error(f"Erro ao extrair memória: {e}")
        
    return "Não consegui extrair o fato com clareza."

def start_brain():
    """Loop Principal"""
    log.info(f"\nConectado à Interface Neural {settings.OLLAMA_MODEL} em {settings.OLLAMA_HOST}")
    
    # Frase inicial clássica
    speak("Importando preferências virtuais... pronto. À sua disposição, senhor.")

    # --- LIGAR MONITORAMENTO ---
    # Verifica a cada 30s o HARDWARE
    sys_monitor.start_proactive_monitor(interval=30)

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