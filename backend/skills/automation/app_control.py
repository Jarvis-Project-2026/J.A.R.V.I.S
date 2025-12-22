import os
import difflib
import subprocess
import json
import psutil
from core import log


# --- CONFIGURAÇÃO DA SKILL ---
INTENT = "APP_CONTROL"
PROMPT_TEXT = """- APP_CONTROL: O usuário quer abrir, fechar ou focar (trazer para frente) um programa específico. 
  Entity = nome do software (ex: 'chrome', 'spotify', 'camera', 'notepad', 'calc' e etc).
  Verbos: abrir, iniciar, fechar, encerrar, focar, mostrar, mudar para, trazer."""

# --- CACHE GLOBAL ---
# Armazena os apps encontrados para não varrer o disco toda vez (Melhora performance)
INSTALLED_APPS_CACHE = {}

# --- ALIASES MANUAIS (Apelidos que a busca automática não resolveria) ---
ALIASES = {
    "zap": "whatsapp",
    "navegador": "opera",
    "vs": "visual studio code",
    "lol": "league of legends",
    "calculadora": "calculator",
    "calc": "calculator"
}

# --- MAPEAMENTO DE PROCESSOS (Nomes reais dos executáveis no Windows) ---
PROCESS_MAP = {
    "calculadora": ["CalculatorApp", "Calculator"],
    "spotify": ["Spotify"],
    "chrome": ["chrome"],
    "opera": ["opera"],
    "calcula": ["CalculatorApp", "Calculator"],
    "calculator": ["CalculatorApp", "Calculator"]
}

def get_installed_apps():
    """
    Varre o Menu Iniciar e usa PowerShell para descobrir o que está instalado.
    Retorna um dict: {'nome do app': 'caminho_ou_id'}
    """
    global INSTALLED_APPS_CACHE
    if INSTALLED_APPS_CACHE:
        return INSTALLED_APPS_CACHE

    log.info("📂 [SKILL] Indexando softwares instalados (Classic + UWP)...")
    
    apps = {}

    # 1. Busca via PowerShell (Pega Apps da Loja e Atalhos Modernos)
    try:
        cmd = 'powershell -Command "Get-StartApps | Select-Object Name, AppID | ConvertTo-Json -Compress"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0 and result.stdout.strip():
            raw_data = json.loads(result.stdout)
            # Se vier só um app, o JSON não é lista. Forçamos a ser.
            data = raw_data if isinstance(raw_data, list) else [raw_data]
            for item in data:
                name = item.get('Name', '').lower().strip()
                appid = item.get('AppID', '')
                if name and appid:
                    apps[name] = appid
    except Exception as e:
        log.error(f"Erro ao indexar via PowerShell: {e}")

    # 2. Busca Clássica via Sistema de Arquivos (Redundância para LNKs órfãos)
    paths = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs")
    ]
    for path in paths:
        if not os.path.exists(path): continue
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(".lnk"):
                    clean_name = file[:-4].lower().strip()
                    if clean_name not in apps: # Prioridade para o AppID do PowerShell
                        apps[clean_name] = os.path.join(root, file)
    
    INSTALLED_APPS_CACHE = apps
    log.info(f"✅ [SKILL] Indexação concluída. {len(apps)} apps encontrados.")
    return apps

def find_best_match(user_query, apps_dict):
    """
    Usa algoritmo de similaridade para encontrar o app mais próximo do que foi falado.
    """
    # 1. Verifica match exato nos Aliases manuais
    if user_query in ALIASES:
        target_alias = ALIASES[user_query]
        # Tenta achar o alias dentro dos apps instalados
        matches = difflib.get_close_matches(target_alias, apps_dict.keys(), n=1, cutoff=0.6)
        if matches:
            return matches[0], apps_dict[matches[0]]

    # 2. Busca Difusa (Fuzzy) na lista de apps reais
    # n=1: queremos apenas o melhor candidato
    # cutoff=0.5: precisa ter pelo menos 50% de semelhança
    matches = difflib.get_close_matches(user_query, apps_dict.keys(), n=1, cutoff=0.5)
    
    if matches:
        best_name = matches[0]
        return best_name, apps_dict[best_name]
    
    return None, None

def find_active_processes(target_name):
    """Retorna lista de processos (psutil.Process) que correspondem ao nome/alias."""
    found_procs = []
    targets_to_check = PROCESS_MAP.get(target_name, [target_name])
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            for t in targets_to_check:
                if t.lower() in proc_name:
                    found_procs.append(proc)
                    break 
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return found_procs

def focus_window(pid):
    """Usa PowerShell para trazer a janela do PID para frente."""
    cmd = f"""
    $p = Get-Process -Id {pid} -ErrorAction SilentlyContinue
    if ($p -and $p.MainWindowTitle) {{
        $w = New-Object -ComObject WScript.Shell
        $w.AppActivate($p.MainWindowTitle)
        return "OK"
    }}
    return "NO_WINDOW"
    """
    try:
        # Executa o PS e captura "OK"
        res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True).stdout.strip()
        return "OK" in res
    except:
        return False

def execute(entity, command_text=""):
    if not entity:
        return "Não entendi qual programa você quer gerenciar."

    target = entity.lower().strip()
    full_cmd = command_text.lower()
    
    # Detecção de Intenções Específicas
    is_closing = any(w in full_cmd for w in ["fechar", "encerre", "finalizar", "mate", "pare"])
    is_focusing = any(w in full_cmd for w in ["focar", "foco", "mostre", "mostrar", "mude", "veja", "traz"])

    # --- 1. LÓGICA DE FOCO (Contextual Window Focus) ---
    if is_focusing:
        log.info(f"� [SKILL] Tentando focar no app: {target}")
        procs = find_active_processes(target)
        
        if not procs:
            return f"O {target} não parece estar aberto no momento. Quer que eu o abra?"
        
        # Tenta focar no primeiro processo que tiver janela
        for proc in procs:
            if focus_window(proc.info['pid']):
                return f"Trazendo o {target} para sua tela."
        
        return f"O {target} está rodando, mas não encontrei uma janela visível para focar."

    # --- 2. LÓGICA DE FECHAMENTO ---
    if is_closing:
        log.info(f"🛑 [SKILL] Tentando encerrar processo relacionado a: {target}")
        procs = find_active_processes(target)
        
        if procs:
            count = 0
            for proc in procs:
                try:
                    proc.terminate()
                    count += 1
                except: pass
            return f"{count} processos do {target} foram encerrados."
        else:
            return f"Não encontrei o processo {target} em execução para encerrar."

    # --- 3. LÓGICA DE ABERTURA ---
    # Verifica se já está aberto antes de abrir de novo (Opcional, mas smart)
    # Se o usuário só disse "abrir spotify" e ele já ta aberto, focar é mais inteligente
    existing_procs = find_active_processes(target)
    if existing_procs:
        # Tenta focar primeiro
        for proc in existing_procs:
            if focus_window(proc.info['pid']):
                return f"O {target} já está aberto. Trouxe ele para frente."

    # Se não tá aberto ou não conseguiu focar, abre do zero
    apps = get_installed_apps()
    app_name, app_path = find_best_match(target, apps)
    
    if app_path:
        try:
            log.info(f"🚀 [SKILL] Abrindo: {app_name} (Target: {app_path})")
            if "!" in app_path or app_path.startswith("{"):
                subprocess.Popen(f'explorer.exe shell:AppsFolder\\{app_path}', shell=True)
            else:
                os.startfile(app_path)
            return f"Iniciando {app_name}."
        except Exception as e:
            log.error(f"Erro ao abrir {app_name}: {e}")
            return f"Erro ao iniciar {app_name}."
    
    # Fallback
    try:
        log.warning(f"⚠️ App '{target}' não encontrado. Tentando 'Run'...")
        subprocess.Popen(target, shell=True)
        return f"Executando comando: {target}"
    except:
        return f"Não encontrei o software '{target}'."