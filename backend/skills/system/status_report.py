import requests
import datetime
import re
from core import log, db
from core.SystemInfo import SystemInfo

# --- CONFIGURAÇÃO DA SKILL ---
INTENT = "SYSTEM_REPORT"
PROMPT_TEXT = """- SYSTEM_REPORT: Monitoramento em tempo real, checkup de saúde e boot protocol.
  Use quando: Usuário perguntar sobre "status", "status do sistema", "relatório de danos" ou "relatório do sistema"."""

# Instanciamos um monitor para leituras
sys_monitor = SystemInfo()

def get_time_greeting(user_name):
    hour = datetime.datetime.now().hour
    if 0 <= hour < 5: 
        return f"Madrugada produtiva, {user_name}?"
    if 5 <= hour < 12: 
        return f"Bom dia, {user_name}."
    if 12 <= hour < 18: 
        return f"Boa tarde, {user_name}."
    return f"Boa noite, {user_name}."

def get_weather_context():
    """Busca dados de clima via Open-Meteo (Sem API Key)."""
    try:
        # Recupera localização da memória ou usa Default (SP)
        # TODO: Implementar geolocalização automática futura
        lat = db.get_memory("latitude") or "-23.5505"
        lon = db.get_memory("longitude") or "-46.6333"
        
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=3)
        
        if res.status_code == 200:
            data = res.json().get('current_weather', {})
            temp = data.get('temperature')
            # Tradução básica de códigos WMO
            wmo_code = data.get('weathercode')
            condition = "céu limpo"
            if wmo_code > 3: condition = "nublado"
            if wmo_code > 50: condition = "chuva leve"
            if wmo_code > 80: condition = "chuva forte"
            
            return f"{temp}°C com {condition}."
    except Exception:
        return None
    return None

def generate_boot_report():
    """Gera um relatório verbal conciso sobre o estado do JARVIS."""
    
    # 1. Recupera identidade
    user_name = db.get_memory("apelido") or "Senhor"
    greeting = get_time_greeting(user_name)
    
    # 2. Leitura de Sensores
    batt = sys_monitor.get_battery_status()
    cpu = sys_monitor.get_cpu_usage()
    ram = sys_monitor.get_ram_usage()
    
    # 3. Análise de Saúde (Triage)
    alerts = []
    
    # Bateria
    batt_desc = f"{batt['percent']}%"
    if not batt['plugged'] and batt['percent'] < 30:
        alerts.append("reservas de energia baixas")
    
    # Carga
    if cpu > 80:
        alerts.append("núcleo de processamento sobrecarregado")
    if ram['percent'] > 90:
        alerts.append("memória saturada")

    # 4. Construção da Narrativa (Estilo Jarvis)
    # Ex: "Boa noite, Senhor. Interface conectada. Capacidade de energia em 100%. Todos os sistemas operando nominalmente."
    
    status_phrases = [greeting]
    
    status_phrases.append(f"Interface conectada.")
    
    if batt['plugged']:
         status_phrases.append(f"Fonte de alimentação externa acoplada. Carga em {batt_desc}.")
    else:
         status_phrases.append(f"Operando na bateria interna com {batt_desc} de capacidade.")
    
    if alerts:
        alert_msg = " e ".join(alerts)
        status_phrases.append(f"Atenção: Detectado {alert_msg}.")
    else:
        status_phrases.append("Todos os subsistemas operando dentro dos parâmetros nominais.")
        
    # Adiciona Clima
    weather = get_weather_context()
    if weather:
        status_phrases.append(f"No ambiente externo: {weather}")
    
    # Adiciona Ping (Latência Neural)
    ping = sys_monitor.get_ping()
    if ping:
        status_phrases.append(f"Latência de conexão neural em {ping}ms.")
    else:
        status_phrases.append(f"Atenção: Link neural offline.")
        
    return " ".join(status_phrases)

def execute(entity, command):
    log.info(f"📊 [STATUS] Executando Protocolo de Relatório.")
    return generate_boot_report()
