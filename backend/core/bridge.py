import webview
import json
from .logger import log


class JarvisAPI:
    """
    Ponte de comunicação Bidirecional:
    - Frontend -> Backend (Comandos do usuário)
    - Backend -> Frontend (Alertas proativos do sistema)
    """
    def __init__(self, system_monitor_instance):
        # Recebe a instância ÚNICA e COMPARTILHADA do monitor (vinda do main.py)
        self.sys_monitor = system_monitor_instance 
        self._window = None

    def set_window(self, window):
        """Referência da janela para comandos e notificações push"""
        self._window = window

    # --- TELEMETRIA EM TEMPO REAL (Consumindo a instância compartilhada) ---
    def get_telemetry(self):
        """
        Retorna os dados de hardware para o LiveTelemetry.jsx.
        Usa o mesmo objeto que o cérebro usa, garantindo consistência.
        """
        try:
            return {
                "cpu": self.sys_monitor.get_cpu_detailed(),
                "ram": self.sys_monitor.get_ram_usage(),
                "gpu": self.sys_monitor.get_gpu_info(),
                "net": self.sys_monitor.get_network_speed(),
                "sys": self.sys_monitor.get_system_general(),
                "battery": self.sys_monitor.get_battery_status(),
                "disk": self.sys_monitor.get_disk_io(),
                "storage": self.sys_monitor.get_disk_space() # Adicionado o novo método
            }
        except Exception as e:
            log.error(f"Erro na ponte de telemetria: {e}")
            return None

    # --- NOTIFICAÇÃO PROATIVA (BACKEND -> UI) ---
    def send_frontend_alert(self, level, message):
        """
        Envia um evento para o React reagir sem o usuário pedir.
        Ex: Pulsar vermelho se level='CRITICAL'
        """
        if self._window:
            # Dispara um CustomEvent no JavaScript
            js_code = f"""
            window.dispatchEvent(new CustomEvent('JARVIS_SYS_ALERT', {{ 
                detail: {{ level: '{level}', message: '{message}' }} 
            }}));
            """
            self._window.evaluate_js(js_code)
            log.info(f"⚡ Alerta enviado para UI: [{level}] {message}")

    # --- CONTROLE DE SISTEMA ---
    def shutdown(self):
        """Fecha a aplicação via interface"""
        log.warning("Comando de desligamento recebido via UI.")
        if self._window:
            self._window.destroy()
            
    def set_hud_state(self, is_critical):
        """
        Sincroniza o estado de emergência do HUD (Vermelho/Azul).
        True = Ativa modo de alerta.
        False = Volta ao normal.
        """
        if self._window:
            state_js = "true" if is_critical else "false"
            # Chama uma função JS específica para alternar classes CSS
            js_code = f"if(window.updateHudState) {{ window.updateHudState({state_js}); }}"
            try:
                self._window.evaluate_js(js_code)
                log.info(f"Visual HUD State alterado para: {'CRITICO' if is_critical else 'NORMAL'}")
            except Exception as e:
                log.error(f"Falha ao atualizar HUD visual: {e}")