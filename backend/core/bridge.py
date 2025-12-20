import webview
from core.logger import log
from core.SystemInfo import SystemInfo

# Instância global interna para a ponte
sys_monitor = SystemInfo()

class JarvisAPI:
    """
    Ponte de comunicação entre o Frontend (React/JS) e o Backend (Python).
    Todas as funções chamadas via window.pywebview.api devem estar aqui.
    """
    def __init__(self):
        self._window = None

    def set_window(self, window):
        """Referência da janela para comandos de controle (ex: fechar)"""
        self._window = window

    # --- TELEMETRIA EM TEMPO REAL ---
    def get_telemetry(self):
        """Retorna os dados de hardware para o LiveTelemetry.jsx"""
        try:
            return {
                "cpu": sys_monitor.get_cpu_detailed(),
                "ram": sys_monitor.get_ram_usage(),
                "gpu": sys_monitor.get_gpu_info(),
                "net": sys_monitor.get_network_speed(),
                "sys": sys_monitor.get_system_general(),
                "battery": sys_monitor.get_battery_status(),
                "disk": sys_monitor.get_disk_io()
            }
        except Exception as e:
            log.error(f"Erro na ponte de telemetria: {e}")
            return None

    # --- CONTROLE DE SISTEMA ---
    def shutdown(self):
        """Fecha a aplicação via interface"""
        log.warning("Comando de desligamento recebido via UI.")
        if self._window:
            self._window.destroy()

    # --- ESPAÇO PARA NOVAS SKILLS VIA API ---
    # Exemplo: def control_lights(self, state): ...