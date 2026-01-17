import os
import time
import json
import requests
import subprocess
import ctypes
from core import log
from core.config import settings

# --- CONFIGURAÇÃO DA SKILL ---
INTENT = "WORK_MACRO"
PROMPT_TEXT = """- WORK_MACRO: Ativar cenas, ambientes ou macros de trabalho/estudo.
  Use quando: O usuário pedir para ativar um 'modo' (ex: Modo Code, Modo Gamer, Modo Estudo) ou preparar o ambiente."""

# --- CÉREBRO ESPECÍFICO DA SKILL (MACRO EXPERT) ---
MACRO_DECISION_PROMPT = """
Você é o Arquiteto de Ambientes do J.A.R.V.I.S.
Sua tarefa é identificar qual MODO o usuário deseja ativar.

MODOS DISPONÍVEIS:
1. "code": Para codificação, desenvolvimento, programação, dev.
2. "estudo": Para leitura, faculdade, cursos, pesquisa.
3. "gamer": Para jogos, steam, entretenimento, game.

SAÍDA: JSON estrito.
{
  "mode": "code" | "estudo" | "gamer" | "outro",
  "reason": "breve explicação"
}
"""

# --- DEFINIÇÃO DAS CENAS ---
SCENES = {
    "code": {
        "apps": ["opera gx", "spotify", "visual studio code", "terminal"],
        "message": "Protocolo de desenvolvimento ativado.",
        "requires_internet": True,
        "playlist": "spotify:playlist:0XkPXLnaDEjO04Z3ZvrHIk" # Só ROCK 
    },
    "estudo": {
        "apps": ["opera gx", "spotify"],
        "message": "Modo de concentração ativado.",
        "requires_internet": True,
        "playlist": "spotify:playlist:5aofQDdd0buo5bRre6yMlG" # MPB
    },
    "gamer": {
        "apps": ["discord", "steam"],
        "message": "Sistemas de entretenimento online. Boa gameplay, senhor.",
        "requires_internet": True,
    }
}

def check_internet():
    """Verifica conectividade básica."""
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

def check_process_running(app_name):
    """
    Verifica se um app já está rodando usando a skill APP_CONTROL se disponível,
    ou psutil como fallback.
    """
    from core import manager
    if "APP_CONTROL" in manager.skills:
        skill = manager.skills["APP_CONTROL"]
        # A skill APP_CONTROL tem a função find_active_processes mas ela é interna.
        # Vamos usar psutil direto aqui para ser mais rápido ou usar a skill se fosse exposta.
        # Como não conseguimos importar 'find_active_processes' fácil sem mexer na outra skill,
        # vamos usar o execute com uma ação de 'check' simulada ou implementar local simples.
        pass
    
    # Implementação local rápida
    import psutil
    for proc in psutil.process_iter(['name']):
        try:
            if app_name.lower() in proc.info['name'].lower():
                return True
        except: pass
    return False

def _ask_ollama_macro_expert(user_text):
    """Consulta o LLM para decidir qual macro ativar."""
    url = f"http://{settings.OLLAMA_HOST}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": user_text,
        "system": MACRO_DECISION_PROMPT,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1}
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("response", "{}")
    except Exception as e:
        log.error(f"❌ [MACRO SKILL] Erro no cérebro (Timeout/Conexão): {e}")
        return None

def execute_app_action(app_name, action="open"):
    """Reutiliza a skill APP_CONTROL para abrir os apps da macro."""
    from core import manager 
    
    if "APP_CONTROL" in manager.skills:
        skill = manager.skills["APP_CONTROL"]
        
        # Tentamos silenciar a saída do processo aberto via variável de ambiente 
        # ou redirecionamento se a skill permitir. 
        # Por enquanto, apenas chamamos; a poluição vem geralmente do Popen sem shell=True
        return skill.execute(app_name, f"{action} {app_name}")
    return f"Não consegui acessar o subsistema de controle de apps para {app_name}."

def toggle_notifications(enabled=True):
    """Ativa ou desativa as notificações do Windows (Foco / DND)."""
    value = 1 if enabled else 0
    try:
        cmd = f'powershell -Command "Set-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings\' -Name \'NOC_GLOBAL_SETTING_TOASTS_ENABLED\' -Value {value}"'
        os.system(cmd)
        log.info(f"🔔 Notificações do sistema {'ativadas' if enabled else 'silenciadas'}.")
        return True
    except Exception as e:
        log.error(f"Erro ao alternar notificações: {e}")
        return False

def organize_windows(mode):
    """
    Organiza as janelas baseando-se na qtde de monitores e no Modo.
    Usa um script PowerShell robusto injetado diretamente.
    """
    log.info("📐 Calculando layout de janelas...")
    
    # Script PowerShell Híbrido: C# para User32.dll + Lógica de Monitores
    ps_script = """
    Add-Type @"
      using System;
      using System.Runtime.InteropServices;
      public class Win32 {
        [DllImport("user32.dll")]
        public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool bRepaint);
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        [DllImport("user32.dll")]
        public static extern bool SetForegroundWindow(IntPtr hWnd);
      }
"@

    # 1. Detectar Monitores
    Add-Type -AssemblyName System.Windows.Forms
    $screens = [System.Windows.Forms.Screen]::AllScreens
    $monitorCount = $screens.Count
    $prim = $screens[0].WorkingArea
    
    # Definição de Alvos (Process Name -> Variável)
    # Tenta pegar processos com janela visível
    $code = Get-Process -Name "Code" -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1
    $browser = Get-Process -Name "opera", "chrome", "msedge" -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1
    $term = Get-Process -Name "WindowsTerminal", "cmd", "powershell" -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1
    $spotify = Get-Process -Name "Spotify" -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1
    
    # --- MODO CODE ---
    if ("%MODE%" -eq "code") {
        if ($monitorCount -eq 1) {
            # 1 Monitor: VS Code (70%), Browser (30%)
            $wCode = [math]::Floor($prim.Width * 0.70)
            $wBrowser = $prim.Width - $wCode
            
            if ($code) { 
                [Win32]::ShowWindow($code.MainWindowHandle, 1) # Ensure Normal State
                [Win32]::MoveWindow($code.MainWindowHandle, $prim.Left, $prim.Top, $wCode, $prim.Height, $true) 
            }
            if ($browser) { 
                [Win32]::ShowWindow($browser.MainWindowHandle, 1)
                [Win32]::MoveWindow($browser.MainWindowHandle, $prim.Left + $wCode, $prim.Top, $wBrowser, $prim.Height, $true) 
            }
        }
        else {
            # 2+ Monitores: VS Code (Monitor 1), Browser (Monitor 2)
            $sec = $screens[1].WorkingArea
            
            if ($code) { 
                [Win32]::ShowWindow($code.MainWindowHandle, 3) # Maximize
                [Win32]::MoveWindow($code.MainWindowHandle, $prim.Left, $prim.Top, $prim.Width, $prim.Height, $true) 
            }
            if ($browser) {
                 [Win32]::ShowWindow($browser.MainWindowHandle, 1) # Normal (para mover entre telas as vezes precisa)
                 [Win32]::MoveWindow($browser.MainWindowHandle, $sec.Left, $sec.Top, $sec.Width, $sec.Height, $true)
                 [Win32]::ShowWindow($browser.MainWindowHandle, 3) # Maximize depois de mover
            }
        }
    }
    
    # --- MODO ESTUDO ---
    if ("%MODE%" -eq "estudo") {
         # Exemplo: Browser Esquerda (50%), Notion Direita (50%)
         # Adaptar conforme necessidade do Notion (geralmente é app web ou desktop name 'Notion')
         $notion = Get-Process -Name "Notion" -ErrorAction SilentlyContinue | Select-Object -First 1
         
         $half = [math]::Floor($prim.Width * 0.5)
         
         if ($browser) { [Win32]::MoveWindow($browser.MainWindowHandle, $prim.Left, $prim.Top, $half, $prim.Height, $true) }
         if ($notion) { [Win32]::MoveWindow($notion.MainWindowHandle, $prim.Left + $half, $prim.Top, $half, $prim.Height, $true) }
    }
    """
    
    # Injeta o modo atual no script
    final_script = ps_script.replace("%MODE%", mode)
    
    try:
        # Executa silenciosamente
        subprocess.Popen(["powershell", "-Command", final_script], shell=True)
        log.info(f"🪟 Layout de janelas aplicado para modo {mode}.")
    except Exception as e:
        log.error(f"Erro ao organizar janelas: {e}")

def execute(entity, command_text=""):
    # Importação Tardia de Speak para Feedback Verbal Imediato
    from services.speak import speak
    
    if not command_text:
        return "Qual protocolo de ambiente devo iniciar, senhor?"

    # 1. Pergunta ao cérebro qual o modo
    ai_response = _ask_ollama_macro_expert(command_text)
    if not ai_response:
        return "Falha na triangulação de dados. Não consigo processar a macro agora."

    try:
        decision = json.loads(ai_response)
        mode = decision.get("mode")

        if mode not in SCENES or mode == "outro":
             return "Esse perfil de ambiente ainda não consta nos meus protocolos, senhor."

        scene = SCENES[mode]
        
        # --- FATOR IMERSÃO: Confirmação Verbal ---
        speak(f"Carregando protocolo {mode}, senhor. Ajustando ambiente.")
        
        # 2. Executa as ações
        log.info(f"🎭 Ativando Cena: {mode.upper()}")

        if mode == "estudo":
            toggle_notifications(enabled=False)
        else:
            toggle_notifications(enabled=True)

        # 3. System Check (Internet)
        if scene.get("requires_internet") and not check_internet():
            return "Senhor, detectei que estamos sem conexão com a internet. Não poderei iniciar este protocolo online."

        # 4. Abre os apps da cena selecionada
        for app in scene["apps"]:
            log.debug(f"Macros: Verificando {app}...")
            execute_app_action(app, action="open")
            time.sleep(1.5) 
            
        # 5. FATOR IMERSÃO: Trilha Sonora
        if "playlist" in scene:
            log.info(f"🎵 Iniciando trilha sonora: {scene['playlist']}")
            spotify_uri = scene['playlist']
            
            # Remove o :play antigo se houver, pois vamos forçar via teclado
            if spotify_uri.endswith(":play"):
                spotify_uri = spotify_uri.replace(":play", "")
            
            # 1. Abre o Spotify na Playlist específica (foca a janela e carrega a lista)
            # O comando 'start' do Windows executa a URI
            os.system(f"start {spotify_uri}")
            
            # 2. Aguarda o Spotify processar (essencial para não dar play no nada)
            # Se o PC for mais lento, aumente para 4 ou 5 segundos
            time.sleep(3) 
            
            # 3. Envia o sinal de tecla "Media Play/Pause" via Windows API
            log.debug("Enviando sinal de Play via Hardware...")
            VK_MEDIA_PLAY_PAUSE = 0xB3
            hwcode = ctypes.windll.user32.MapVirtualKeyA(VK_MEDIA_PLAY_PAUSE, 0)
            
            # Pressiona a tecla
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, hwcode, 0, 0)
            # Solta a tecla
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, hwcode, 2, 0)

        # 6. Organiza as janelas
        time.sleep(3) 
        organize_windows(mode)
        
        return f"{scene['message']} Sistema pronto."

    except Exception as e:
        log.error(f"Erro na Skill de Macros: {e}")
        return "Detectada instabilidade ao tentar configurar o ambiente de trabalho."
