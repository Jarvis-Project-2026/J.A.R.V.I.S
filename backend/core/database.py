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
        """Cria a estrutura de tabelas (Config, Histórico e Hardware)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 1. Config (Estado da aplicação: skills ativas/inativas, preferências de UI)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 2. Histórico (Logs de Conversa com session_id)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL DEFAULT 'default',
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 3. Hardware (Identidade da Máquina)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hardware (
                    component TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 4. Sessions (Título customizado e Fixação de Chats)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    is_pinned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Migração automática e retrocompatível: garante que banco existente ganhe a coluna session_id
            cursor.execute("PRAGMA table_info(history)")
            columns = [col[1] for col in cursor.fetchall()]
            if "session_id" not in columns:
                cursor.execute("ALTER TABLE history ADD COLUMN session_id TEXT NOT NULL DEFAULT 'default'")
                log.info("Migração de banco executada: coluna 'session_id' adicionada à tabela history.")

            # Garante que bancos com a tabela antiga ganhem a coluna is_pinned
            cursor.execute("PRAGMA table_info(sessions)")
            session_cols = [col[1] for col in cursor.fetchall()]
            if "is_pinned" not in session_cols:
                cursor.execute("ALTER TABLE sessions ADD COLUMN is_pinned INTEGER DEFAULT 0")
                log.info("Migração de banco executada: coluna 'is_pinned' adicionada à tabela sessions.")

            # Cria índice na coluna session_id para consultas super rápidas (agora que a coluna 100% existe)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_session ON history(session_id)')

            conn.commit()
            log.info("Banco de dados verificado (Tabelas: Config, History, Hardware, Sessions).")
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

    # --- MÉTODOS DE CONFIG (Estado da aplicação: skills, preferências de UI) ---
    def save_config(self, key: str, value: Any):
        conn = self._get_connection()
        cursor = conn.cursor()

        if not isinstance(value, str):
            value = json.dumps(value)

        try:
            cursor.execute('''
                INSERT INTO config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=CURRENT_TIMESTAMP
            ''', (key, value))
            conn.commit()
            log.debug(f"Config persistida: [{key}]")
        except sqlite3.Error as e:
            log.error(f"Falha ao salvar config '{key}': {e}")
        finally:
            conn.close()

    def get_config(self, key: str) -> Optional[Any]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
            result = cursor.fetchone()
            if result:
                data = result[0]
                try:
                    return json.loads(data)
                except Exception:
                    return data
            return None
        except sqlite3.Error as e:
            log.error(f"Erro ao ler config '{key}': {e}")
            return None
        finally:
            conn.close()

    # --- MÉTODOS DE HISTÓRICO ---
    def log_interaction(self, role: str, content: str, session_id: str = 'default'):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO history (role, content, session_id) VALUES (?, ?, ?)', (role, content, session_id))
            conn.commit()
        except sqlite3.Error as e:
            log.error(f"Falha ao registrar histórico para sessão '{session_id}': {e}")
        finally:
            conn.close()

    def delete_history_from(self, session_id: str, message_id: int):
        """Apaga todos os logs de conversa de uma sessão a partir de um ID de mensagem específico."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM history WHERE session_id = ? AND id >= ?', (session_id, message_id))
            conn.commit()
            log.info(f"Limpeza de histórico executada no SQLite: deletadas mensagens a partir de '{message_id}' na sessão '{session_id}'.")
        except sqlite3.Error as e:
            log.error(f"Falha ao deletar histórico para sessão '{session_id}' a partir de '{message_id}': {e}")
        finally:
            conn.close()

    def update_history_message(self, message_id: int, new_content: str):
        """Atualiza o conteúdo de uma mensagem específica no banco de dados."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE history SET content = ? WHERE id = ?', (new_content, message_id))
            conn.commit()
            log.info(f"Mensagem '{message_id}' atualizada no SQLite com o novo prompt.")
        except sqlite3.Error as e:
            log.error(f"Falha ao atualizar mensagem '{message_id}': {e}")
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
            log.error(f"Erro na busca de histórico: {e}")
            return []
        finally:
            conn.close()

# Instância Singleton global
db = DatabaseManager()