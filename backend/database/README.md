# 🗄️ Camada de Persistência (Database J.A.R.V.I.S.)

Este diretório contém a lógica de memória de longo prazo do assistente, utilizando o **SQLite3** nativo como motor de banco de dados. A arquitetura foi desenhada para oferecer **Persistência Transparente**, permitindo que o sistema salve estados e históricos sem bloquear o processamento de áudio ou IA.

## 📋 Estrutura de Dados (Esquema ASCII)

O banco de dados `jarvis_memory.db` é composto por duas tabelas fundamentais que separam fatos estáticos de interações dinâmicas:

### 1. Tabela `memory` (Memória Semântica)

Utilizada para armazenar fatos, preferências e configurações que devem persistir entre reinicializações.

```text
+-------------------+------------------+---------------------+
|      key (PK)     |      value       |     updated_at      |
|       [TEXT]      |      [TEXT]      |     [TIMESTAMP]     |
+-------------------+------------------+---------------------+
| "user_name"       | "Tony Stark"     | 2025-12-18 10:00:00 |
| "favorite_color"  | "Azul"           | 2025-12-18 10:05:20 |
+-------------------+------------------+---------------------+

```

* **`key`**: Identificador único (Primary Key).
* **`value`**: Conteúdo serializado em JSON para suportar listas e dicionários complexos.
* **`updated_at`**: Registro automático de modificação.

### 2. Tabela `history` (Memória Episódica)

Registra a trilha completa de conversação para auditoria e futuro contexto de IA.

```text
+---------+-------------+--------------------------------+--------------------+
| id (PK) |    role     |            content             |      timestamp     |
|  [INT]  |   [TEXT]    |             [TEXT]             |     [TIMESTAMP]    |
+---------+-------------+--------------------------------+--------------------+
|    1    | "user"      | "Olá, Jarvis. Status?"         | 2025-12-18 10:30:01|
|    2    | "assistant" | "Sistemas online, Senhor."     | 2025-12-18 10:30:05|
+---------+-------------+--------------------------------+--------------------+

```

* **`role`**: Define a origem da mensagem (`user` ou `assistant`).
* **`content`**: Transcrição integral da fala.

## ⚙️ Funcionamento Integrado e Manutenção

Para desenvolvedores que realizarão manutenção no sistema, é vital entender estas quatro integrações:

1. **Inicialização Automática**: O `DatabaseManager` realiza um *Sanity Check* no boot, criando o arquivo e as tabelas caso não existam no caminho `settings.DB_PATH`.
2. **Lógica de UPSERT**: O método `save_memory` utiliza a cláusula `ON CONFLICT(key) DO UPDATE`, garantindo que chaves duplicadas não gerem erros, apenas atualizem o valor existente.
3. **Observabilidade**: Todas as transações são reportadas ao `logger.py`. Escritas bem-sucedidas geram logs de `DEBUG`, enquanto falhas de I/O geram logs de `ERROR` ou `CRITICAL`.
4.**Ciclo de Vida no `main.py**`:

* **Boot**: Consulta `user_name` para saudação personalizada.
* **Input**: Grava imediatamente o comando reconhecido pelo `listen()`.
* **Output**: Grava a resposta gerada pelo `execute_command()` antes da síntese de voz.

## 🛠️ Especificações Técnicas

* **Motor**: SQLite3 nativo.
* **Encoding**: UTF-8 para suporte total a caracteres da língua portuguesa.
* **Localização**: Definida dinamicamente no `config.py` dentro da pasta `backend/database/`.

---

**Gostaria que eu gerasse agora a documentação técnica para o arquivo `SystemInfo.py` para completar o manual de hardware do J.A.R.V.I.S.?**
