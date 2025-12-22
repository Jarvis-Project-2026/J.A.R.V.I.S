import sqlite3
import json
from typing import Any, Optional, Dict
from .logger import log
from .config import settings

class DatabaseManager:
    """Gerencia a persistência de dados do JARVIS (Memória de Longo Prazo e Identidade)."""
    
    def __init__(self):
        self.db_path = settings.DB_PATH
        self._initialize_tables()

    def _get_connection(self):
        """Cria uma conexão robusta com o banco de dados."""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            log.critical(f"Falha catastrófica ao conectar ao banco de dados: {e}")
            raise

    def _initialize_tables(self):
        """Cria a estrutura de tabelas (Memória, Histórico e Hardware)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Memória (Preferências/Fatos)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. Histórico (Logs de Conversa)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 3. Hardware (Identidade da Máquina) - NOVA TABELA
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hardware (
                    component TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            log.info("Banco de dados verificado (Tabelas: Memory, History, Hardware).")
        except sqlite3.Error as e:
            log.error(f"Erro ao criar estrutura do banco de dados: {e}")
        finally:
            conn.close()

    # --- MÉTODOS DE HARDWARE ---
    def update_hardware_spec(self, component: str, description: str):
        """
        Salva uma especificação de hardware.
        Ex: component='CPU', description='Intel Core i9-9900K'
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO hardware (component, description, detected_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(component) DO UPDATE SET 
                    description=excluded.description, 
                    detected_at=CURRENT_TIMESTAMP
            ''', (component, description))
            conn.commit()
        except sqlite3.Error as e:
            log.error(f"Erro ao salvar spec de hardware '{component}': {e}")
        finally:
            conn.close()

    def get_system_specs(self) -> str:
        """
        Retorna todas as specs formatadas como um texto único para o Prompt do Sistema.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT component, description FROM hardware')
            rows = cursor.fetchall()
            
            if not rows:
                return "Especificações de sistema ainda não catalogadas."

            # Formata bonito para o J.A.R.V.I.S ler
            specs_text = "ESPECIFICAÇÕES DO SISTEMA HOSPEDEIRO:\n"
            for component, desc in rows:
                specs_text += f"- {component}: {desc}\n"
            
            return specs_text
        except sqlite3.Error as e:
            log.error(f"Erro ao ler hardware: {e}")
            return "Erro ao recuperar especificações."
        finally:
            conn.close()

    # --- MÉTODOS DE MEMÓRIA (KEY-VALUE) ---
    def save_memory(self, key: str, value: Any):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if not isinstance(value, str):
            value = json.dumps(value)

        try:
            cursor.execute('''
                INSERT INTO memory (key, value, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET 
                    value=excluded.value, 
                    updated_at=CURRENT_TIMESTAMP
            ''', (key, value))
            conn.commit()
            log.debug(f"Memória persistida: [{key}]")
        except sqlite3.Error as e:
            log.error(f"Falha ao salvar memória '{key}': {e}")
        finally:
            conn.close()

    def get_memory(self, key: str) -> Optional[Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT value FROM memory WHERE key = ?', (key,))
            result = cursor.fetchone()
            if result:
                data = result[0]
                try:
                    return json.loads(data)
                except:
                    return data
            return None
        except sqlite3.Error as e:
            log.error(f"Erro ao ler memória '{key}': {e}")
            return None
        finally:
            conn.close()

    # --- MÉTODOS DE HISTÓRICO ---
    def log_interaction(self, role: str, content: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO history (role, content) VALUES (?, ?)', (role, content))
            conn.commit()
        except sqlite3.Error as e:
            log.error(f"Falha ao registrar histórico: {e}")
        finally:
            conn.close()
            
    def search_relevant_context(self, query: str, limit: int = 3):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stop_words = ["qual", "voce", "sobre", "meu", "minha", "como", "quem", "jarvis"]
        search_terms = [w for w in query.split() if len(w) > 3 and w.lower() not in stop_words]
        
        if not search_terms: return []

        search_query = " OR ".join(["content LIKE ?" for _ in search_terms])
        params = [f"%{term}%" for term in search_terms] + [limit]

        try:
            cursor.execute(f"SELECT role, content FROM history WHERE ({search_query}) ORDER BY timestamp DESC LIMIT ?", params)
            return cursor.fetchall()
        except Exception as e:
            log.error(f"Erro na busca de memória: {e}")
            return []
        finally:
            conn.close()

# Instância Singleton global
db = DatabaseManager()