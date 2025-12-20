import sqlite3
import json
from typing import Any, Optional
from .logger import log
from .config import settings

class DatabaseManager:
    """
    Gerencia a persistência de dados do JARVIS (Memória de Longo Prazo).
    Utiliza SQLite para simplicidade e performance local.
    """
    
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
        """Cria a estrutura de tabelas seguindo a filosofia Fail-Fast."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabela de Memória (Chave-Valor) - Para preferências e fatos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabela de Histórico - Para auditoria e contexto de IA
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            log.info("Banco de dados inicializado e tabelas verificadas.")
        except sqlite3.Error as e:
            log.error(f"Erro ao criar estrutura do banco de dados: {e}")
        finally:
            conn.close()

    # --- MÉTODOS DE MEMÓRIA (KEY-VALUE) ---
    def save_memory(self, key: str, value: Any):
        """Salva ou atualiza um dado (UPSERT). Aceita strings, dicts e listas."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Converte objetos complexos para JSON para armazenamento
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
        """Recupera um dado. Tenta decodificar JSON se necessário."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT value FROM memory WHERE key = ?', (key,))
            result = cursor.fetchone()
            if result:
                data = result[0]
                try:
                    return json.loads(data) # Tenta converter de volta se for JSON
                except:
                    return data # Retorna como string se não for JSON
            return None
        except sqlite3.Error as e:
            log.error(f"Erro ao ler memória '{key}': {e}")
            return None
        finally:
            conn.close()

    # --- MÉTODOS DE HISTÓRICO ---

    def log_interaction(self, role: str, content: str):
        """Registra permanentemente a conversa entre Usuário e JARVIS."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO history (role, content) VALUES (?, ?)', (role, content))
            conn.commit()
            # Log de debug para não poluir o terminal, mas registrar no arquivo
            log.debug(f"Interação registrada no histórico: {role}")
        except sqlite3.Error as e:
            log.error(f"Falha ao registrar histórico: {e}")
        finally:
            conn.close()
            
    def search_relevant_context(self, query: str, limit: int = 3):
        """Busca no histórico trechos relevantes para a pergunta atual."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Palavras que não ajudam na busca
        stop_words = ["qual", "voce", "sobre", "meu", "minha", "como", "quem", "jarvis"]
        search_terms = [w for w in query.split() if len(w) > 3 and w.lower() not in stop_words]
        
        if not search_terms: return []

        # Busca flexível com LIKE
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