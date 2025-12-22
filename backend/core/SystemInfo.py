import psutil
import platform
import time
import threading
from datetime import datetime, timedelta
from .config import settings
from .logger import log

# --- BLINDAGEM DE GPU ---
try:
    import GPUtil
    HAS_GPU_LIB = True
except Exception as e:
    HAS_GPU_LIB = False
# ------------------------

class SystemInfo:
    def __init__(self, brain_callback=None):
        self.os_name = platform.system()
        self.brain_callback = brain_callback
        self.is_monitoring = False
        self.in_critical_state = False # Rastreia se o HUD está vermelho atualmente
        
        # --- CONFIGURAÇÃO DE LIMITES DE HARDWARE ---
        self.thresholds = {
            'cpu_max': 90.0,
            'ram_max': 90.0,
            'gpu_temp_max': 75.0,
            'disk_space_min': 10.0,
            'battery_min': 15.0
        }

        # Estado anterior (Debounce)
        self.alert_state = {
            'cpu': False,
            'ram': False,
            'gpu': False,
            'disk': False,
            'battery': 100
        }
        
        # Armazena QUANDO foi o último aviso (Timestamp)
        self.last_alert_time = {
            'cpu': 0,
            'ram': 0,
            'gpu': 0,
            'disk': 0
        }
        
        # Cooldown: Tempo em segundos para repetir o alerta (120s = 2 min)
        self.REMINDER_COOLDOWN = 120

        # Inicializa leituras
        psutil.cpu_percent(interval=None)
        self.last_time = time.time()
        
        # Rede e Disco iniciais
        net = psutil.net_io_counters()
        self.last_net_sent = net.bytes_sent
        self.last_net_recv = net.bytes_recv
        
        disk = psutil.disk_io_counters()
        self.last_disk_read = disk.read_bytes if disk else 0
        self.last_disk_write = disk.write_bytes if disk else 0

    def _get_size(self, bytes, suffix="B"):
        """Formata bytes para KB, MB, GB de forma legível."""
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor
            
    def get_disk_space(self):
        """Novo: Verifica espaço em disco (Crítico para saúde do sistema)"""
        try:
            disk = psutil.disk_usage('/')
            free_percent = 100 - disk.percent
            return {"total": self._get_size(disk.total), "free_percent": free_percent}
        except: return {"total": "0B", "free_percent": 100}

    # --- MÉTODOS EXIGIDOS PELO BRAIN.PY (Restaurados) ---
    def get_cpu_usage(self):
        """Retorna apenas a porcentagem simples (float)."""
        return psutil.cpu_percent(interval=None)

    def get_battery_status(self):
        """Retorna status da bateria formatado."""
        if not hasattr(psutil, "sensors_battery"):
            return {"percent": 100, "plugged": True, "time_left": "Desktop"}

        try:
            battery = psutil.sensors_battery()
            if battery:
                if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
                    time_left = "Carregada"
                elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
                    time_left = "Calculando..."
                else:
                    time_left = str(timedelta(seconds=battery.secsleft)).split('.')[0]

                return {
                    "percent": round(battery.percent),
                    "plugged": battery.power_plugged,
                    "time_left": time_left
                }
        except Exception:
            pass
        return {"percent": 100, "plugged": True, "time_left": "Desktop"}
    # ----------------------------------------------------

    def get_cpu_detailed(self):
        """Retorna uso, frequência e núcleos."""
        freq = psutil.cpu_freq()
        return {
            "usage": psutil.cpu_percent(interval=None),
            "cores_logical": psutil.cpu_count(logical=True),
            "cores_physical": psutil.cpu_count(logical=False),
            "freq_current": f"{freq.current:.0f}Mhz" if freq else "N/A"
        }

    def get_ram_usage(self):
        try:
            ram = psutil.virtual_memory()
            return {
                "percent": ram.percent,
                "used": self._get_size(ram.used),
                "total": self._get_size(ram.total),
                "used_gb": round(ram.used / (1024 ** 3), 2) # Adicionado para compatibilidade
            }
        except:
            return {"percent": 0, "used": "0B", "total": "0B", "used_gb": 0}

    def get_gpu_info(self):
        if not HAS_GPU_LIB:
            return {"name": "N/A", "load": 0, "temp": 0, "memory_used": 0}

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    "name": gpu.name,
                    "load": round(gpu.load * 100, 1),
                    "temp": gpu.temperature,
                    "memory_total": f"{gpu.memoryTotal}MB",
                    "memory_used": f"{gpu.memoryUsed}MB"
                }
        except:
            pass
        return {"name": "Integrada/N/A", "load": 0, "temp": 0}

    def get_network_speed(self):
        current_time = time.time()
        time_delta = current_time - self.last_time
        if time_delta <= 0: time_delta = 1 

        net = psutil.net_io_counters()
        
        sent_per_sec = (net.bytes_sent - self.last_net_sent) / time_delta
        recv_per_sec = (net.bytes_recv - self.last_net_recv) / time_delta
        
        self.last_net_sent = net.bytes_sent
        self.last_net_recv = net.bytes_recv

        return {
            "upload_speed": self._get_size(sent_per_sec) + "/s",
            "download_speed": self._get_size(recv_per_sec) + "/s",
            "total_sent": self._get_size(net.bytes_sent),
            "total_recv": self._get_size(net.bytes_recv)
        }

    def get_disk_io(self):
        current_time = time.time()
        time_delta = current_time - self.last_time
        if time_delta <= 0: time_delta = 1

        try:
            disk = psutil.disk_io_counters()
            if not disk: return {"read": "0B/s", "write": "0B/s"}

            read_per_sec = (disk.read_bytes - self.last_disk_read) / time_delta
            write_per_sec = (disk.write_bytes - self.last_disk_write) / time_delta

            self.last_disk_read = disk.read_bytes
            self.last_disk_write = disk.write_bytes
            
            self.last_time = current_time

            return {
                "read_speed": self._get_size(read_per_sec) + "/s",
                "write_speed": self._get_size(write_per_sec) + "/s"
            }
        except:
             return {"read_speed": "0B/s", "write_speed": "0B/s"}

    def get_system_general(self):
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        uptime = datetime.now() - bt
        uptime_str = str(uptime).split('.')[0] 

        return {
            "uptime": uptime_str,
            "processes": len(psutil.pids()),
            "boot_time": bt.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_top_processes(self, resource_type, limit=5):
        """
        Retorna uma lista com os TOP 'limit' processos consumidores.
        resource_type: 'cpu' ou 'memory'
        """
        try:
            if resource_type == 'cpu':
                # --- CORREÇÃO PARA O ZERO POR CENTO ---
                # A CPU precisa de um intervalo (delta) para ser medida.
                
                # Coleta todos os processos vivos
                procs = [p for p in psutil.process_iter(['pid', 'name'])]
                
                # Primeira chamada (Inicia o contador interno do psutil, retorna 0.0)
                for p in procs:
                    try:
                        p.cpu_percent()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Pequena pausa para acumular dados de uso (0.1s é imperceptível para o usuário)
                time.sleep(0.1)
                
                # Segunda chamada (Retorna a média de uso durante a pausa)
                cpu_data = []
                for p in procs:
                    try:
                        # Pega o valor real agora
                        usage = p.cpu_percent()
                        name = p.info['name']
                        
                        # Filtra ruído (0%) e remove o "System Idle Process" (Ocioso) para não confundir o Juiz
                        if usage > 0.0 and name != "System Idle Process":
                            cpu_data.append((name, usage))
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                
                # Ordena pelo maior uso
                top_cpu = sorted(cpu_data, key=lambda x: x[1], reverse=True)[:limit]
                
                # Formata para texto
                return [f"{name} ({val:.1f}%)" for name, val in top_cpu]

            elif resource_type == 'memory':
                # Memória é instantânea, a lógica anterior funciona bem
                key_func = lambda p: p.info['memory_percent']
                attrs = ['pid', 'name', 'memory_percent']
                
                processes = sorted(
                    psutil.process_iter(attrs),
                    key=key_func,
                    reverse=True
                )[:limit]

                result = []
                for proc in processes:
                    result.append(f"{proc.info['name']} ({proc.info['memory_percent']:.1f}%)")
                    
                return result
            
            else:
                return []

        except Exception as e:
            log.error(f"Erro ao buscar processos top ({resource_type}): {e}")
            return []
    
    # --- MONITORAMENTO PROATIVO E CONSTANTE ---
    def start_proactive_monitor(self, interval=10):
        """Inicia a thread de vigilância que roda em paralelo."""
        if self.is_monitoring: return
        self.is_monitoring = True
        # daemon=True: a thread morre quando o programa principal fecha
        thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        thread.start()
        log.info(f"🛡️ Monitoramento de Infraestrutura Iniciado ({interval}s)")

    def _monitor_loop(self, interval):
        """
        Loop de vigilância:
        - Responsabilidade 1 (Rápida): Alternar estado visual do HUD (Vermelho/Normal).
        - Responsabilidade 2 (Lenta): Gerar relatório verbal detalhado respeitando Cooldowns.
        """
        while self.is_monitoring:
            warnings = []
            now = time.time()
            
            try:
                # --- 1. COLETA DE DADOS (Leve) ---
                cpu = self.get_cpu_usage()
                ram = self.get_ram_usage()
                gpu = self.get_gpu_info()
                bat = self.get_battery_status()
                disk = self.get_disk_space()
                
                # --- 2. CHECAGEM DE LIMITES (Booleanos) ---
                is_cpu_high = cpu > self.thresholds['cpu_max']
                is_ram_high = ram['percent'] > self.thresholds['ram_max']
                is_gpu_hot = gpu['temp'] > self.thresholds['gpu_temp_max']
                is_disk_full = disk['free_percent'] < self.thresholds['disk_space_min']
                
                # Bateria crítica: só se não estiver carregando e abaixo do mínimo
                is_battery_crit = (not bat['plugged'] and bat['percent'] <= self.thresholds['battery_min'])
                
                # Estado Geral: Existe ALGUM problema agora?
                current_danger = is_cpu_high or is_ram_high or is_gpu_hot or is_disk_full or is_battery_crit

                # --- 3. LÓGICA VISUAL (HUD RESPONSIVO) ---
                # Detecta mudança de estado: Entrou em perigo OU Saiu do perigo
                if current_danger != self.in_critical_state:
                    self.in_critical_state = current_danger
                    
                    if self.brain_callback:
                        # Envia sinal puro de estado (sem texto para fala)
                        status_code = "CRITICAL_START" if current_danger else "CRITICAL_END"
                        try:
                            # is_status_signal=True garante que o JARVIS não tente "falar" esse código
                            self.brain_callback(status_code, is_proactive=True, is_status_signal=True)
                        except TypeError:
                            # Fallback caso o callback antigo não aceite o parametro is_status_signal
                            # (Segurança para não quebrar se o main.py não estiver atualizado)
                            pass
                        except Exception as e:
                            log.error(f"Erro ao atualizar HUD Visual: {e}")

                # --- 4. LÓGICA VERBAL (MANTENDO SUA LÓGICA ORIGINAL) ---
                # Só entra aqui se houver perigo, economizando processamento
                if current_danger:
                    
                    # CPU Check (Com a sua lógica de Top 5)
                    if is_cpu_high:
                        if (now - self.last_alert_time['cpu'] > self.REMINDER_COOLDOWN):
                            top_list = self.get_top_processes('cpu', limit=5)
                            culprit_txt = f" (Top 5: {', '.join(top_list)})" if top_list else ""
                            warnings.append(f"Processador em {cpu}%{culprit_txt}")
                            self.last_alert_time['cpu'] = now
                    else:
                        # Reseta o timer se o problema sumiu (para avisar logo se voltar)
                        self.alert_state['cpu'] = False 

                    # RAM Check
                    if is_ram_high:
                        if (now - self.last_alert_time['ram'] > self.REMINDER_COOLDOWN):
                            top_list = self.get_top_processes('memory', limit=5)
                            culprit_txt = f" (Consumo: {', '.join(top_list)})" if top_list else ""
                            warnings.append(f"RAM crítica: {ram['percent']}%{culprit_txt}")
                            self.last_alert_time['ram'] = now

                    # GPU Check
                    if is_gpu_hot:
                        if (now - self.last_alert_time['gpu'] > self.REMINDER_COOLDOWN):
                            warnings.append(f"GPU superaquecendo a {gpu['temp']}°C")
                            self.last_alert_time['gpu'] = now

                    # Disk Check
                    if is_disk_full:
                        if (now - self.last_alert_time['disk'] > self.REMINDER_COOLDOWN):
                            warnings.append(f"Disco cheio ({disk['free_percent']:.1f}% livre)")
                            self.last_alert_time['disk'] = now

                    # Battery Check
                    if is_battery_crit:
                        last_bat = self.alert_state['battery'] if isinstance(self.alert_state['battery'], int) else 100
                        if bat['percent'] <= last_bat - 5: # Avisa a cada 5% de queda
                            warnings.append(f"Bateria crítica: {bat['percent']}%")
                            self.alert_state['battery'] = bat['percent']

                    # --- DISPARO DO ALERTA VERBAL ---
                    if warnings and self.brain_callback:
                        alert_msg = ". ".join(warnings)
                        full_context = f"[SISTEMA CRÍTICO] {alert_msg}"
                        try:
                            # is_status_signal=False -> Isso é fala normal
                            self.brain_callback(full_context, is_proactive=True, is_status_signal=False)
                        except TypeError:
                            # Fallback de compatibilidade
                            self.brain_callback(full_context, is_proactive=True)
                        except Exception as e:
                            log.error(f"Erro no envio de alerta verbal: {e}")

            except Exception as e:
                log.error(f"Erro fatal no loop de monitoramento: {e}")
                # Não dá break, apenas loga e tenta na próxima iteração (Resiliência)
            
            time.sleep(interval)