import psutil
import platform
import time
from datetime import datetime, timedelta
from .config import settings

# --- BLINDAGEM DE GPU ---
try:
    import GPUtil
    HAS_GPU_LIB = True
except Exception as e:
    HAS_GPU_LIB = False
# ------------------------

class SystemInfo:
    def __init__(self):
        self.os_name = platform.system()
        # Inicializa CPU (primeira leitura é descarte)
        psutil.cpu_percent(interval=None)
        
        # --- ESTADO PARA CÁLCULO DE VELOCIDADE (NET/DISCO) ---
        self.last_time = time.time()
        
        # Rede inicial
        net = psutil.net_io_counters()
        self.last_net_sent = net.bytes_sent
        self.last_net_recv = net.bytes_recv
        
        # Disco inicial
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