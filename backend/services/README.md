# 🧠 Documentação do Módulo Services

Este diretório contém a lógica neural e sensorial do sistema J.A.R.V.I.S., orquestrando **Input (Audição)**, **Processamento Cognitivo (Cérebro)** e **Output (Fala)**.

## 📂 Estrutura de Arquivos

| Arquivo         | Função                                                                                                    | Principais Dependências                   |
| --------------- | --------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **`brain.py`**  | **Núcleo Cognitivo.** Gerencia intenções, hardware, memória de longo prazo e conexões com a LLM (Ollama). | `core`, `ollama`, `sqlite3`, `subprocess` |
| **`listen.py`** | **Entrada Sensorial.** Captura de áudio, detecção de _Wake Word_ e transcrição (STT).                     | `core`, `speech_recognition`, `re`        |
| **`speak.py`**  | **Saída Sensorial.** Síntese de voz (TTS) híbrida com gerenciamento de concorrência (Thread-Safe).        | `core`, `edge_tts`, `pygame`, `pyttsx3`   |

---

## 1. `brain.py` (O Maestro)

O cérebro deixou de ser um script linear e tornou-se um **Roteador Semântico**. Ele não apenas reage, mas "pensa" antes de agir, classificando a intenção do usuário e gerenciando a identidade da máquina em tempo real.

### 🌟 Novas Funcionalidades Arquiteturais

#### A. Roteador de Intenção (`classify_intent`)

Em vez de buscar palavras-chave soltas (if/else), o sistema envia a frase para a LLM (em modo JSON) para classificar a demanda em 5 categorias estritas:

1. **SHUTDOWN:** Encerramento de protocolos.
2. **HARDWARE:** Perguntas sobre specs, benchmarks ou status do PC.
3. **MEMORY_READ:** Usuário perguntando sobre fatos passados.
4. **MEMORY_WRITE:** Usuário pedindo para gravar uma nova informação.
5. **CHAT:** Conversa genérica/criativa.

#### B. Identidade de Hardware Persistente (`scan_system_hardware`)

Ao iniciar, o sistema executa uma **varredura via PowerShell** para identificar a máquina hospedeira (CPU, GPU Real, RAM, Placa Mãe).

- Esses dados são salvos no banco de dados SQLite (`core.database`).
- **Anti-Alucinação:** Se o usuário pergunta "Qual meu PC?", o sistema injeta esses dados reais no Prompt do Sistema, impedindo a IA de inventar configurações.

#### C. Monitoramento Proativo com "Cache do Juiz"

O sistema monitora recursos em background (`sys_monitor`). Para evitar spam de alertas:

- **O Juiz:** Quando um processo consome muita CPU, a IA decide se é perigoso ou seguro (ex: Jogos = Seguro).
- **O Cache:** Essa decisão é salva em memória (`PROCESS_JUDGEMENT_CACHE`). Se o "Chrome" já foi julgado, o sistema não gasta tokens perguntando novamente.

#### D. Prompt Dinâmico (`ask_local_ai`)

O Contexto do Sistema é montado em tempo real (_Injeção de Dependência de Contexto_):

- **Se Intenção == HARDWARE:** Injeta tabela técnica do banco de dados.
- **Se Intenção == MEMORY_READ:** Injeta fatos recuperados do SQLite.
- **Temperatura Variável:** Usa temperatura `0.1` (fria) para dados técnicos e `0.7` (quente) para conversas casuais.

---

## 2. `listen.py` (Os Ouvidos)

Responsável pela **transcrição de áudio para texto (STT)**. Mantém a lógica de "Janela de Atenção" para conversas fluidas.

### Funcionalidades Chave

- **Wake Word Flexível:** Detecta variações como _'jarvis', 'jar', 'jair', 'jarbas'_. Utiliza Regex (`\bword\b`) para limpar o nome da frase antes do processamento.
- **Janela de Atenção (Active Mode):**
- Ao ouvir o nome, ativa um **Timer de 60 segundos**.
- Durante este tempo, não é necessário repetir "Jarvis".

- **Controle de Loop de Áudio:**
- Expõe métodos `ear_pause()` e `ear_resume()`.
- O `brain.py` usa isso para "tapar os ouvidos" enquanto o próprio JARVIS está falando, evitando que ele ouça a própria voz.

- **Calibração Automática:** Ajusta o limiar de ruído ambiente no primeiro segundo de execução.

---

## 3. `speak.py` (A Voz)

Responsável pela **síntese de texto para áudio (TTS)**. Atualizado para ser _Thread-Safe_ e visualmente interativo.

### Funcionalidades Chave:

**Arquitetura Híbrida (Failover):** 1.**Online (EdgeTTS):** Tenta gerar áudio neural de alta qualidade (`pt-BR-AntonioNeural`). Verifica integridade do arquivo (tamanho > 100 bytes). 2.**Offline (Pyttsx3):** Se a internet cair ou o arquivo falhar, assume o motor robótico local imediatamente.

- **Thread Safety (`speech_lock`):**
- Implementa um `threading.Lock()` para impedir que múltiplas requisições de fala se sobreponham (ex: um alerta de sistema tentando falar em cima de uma resposta de chat).

- **Feedback Visual:**
- Executa o efeito de "datilografia" (`typewriter_effect`) no terminal em uma Thread separada, sincronizada com o áudio.

- **Tratamento de Gírias:**
- Expande abreviações (`vc` -> `você`, `tmj` -> `tamo junto`) via Regex antes de enviar para o motor de voz.

- **Gerenciamento de Arquivos:** Usa `uuid` para arquivos temporários, evitando conflitos de permissão de arquivo no Windows.

---

## ⚙️ Fluxo de Dados (Pipeline)

1. **Inicialização:** `brain.py` varre o hardware via PowerShell -> Salva no SQLite.
2. **Input:** `listen.py` detecta voz -> Transcreve para Texto.
3. **Decisão:** `brain.py` -> `classify_intent()` -> Ollama (JSON Mode).
4. **Roteamento:**

- _Se for Hardware:_ Busca specs no SQLite -> Injeta no Prompt -> Responde.
- _Se for Memória:_ Grava ou Busca no SQLite -> Responde.
- _Se for Chat:_ Busca telemetria tempo real (`SystemInfo`) -> Responde.

  5.**Output:** `speak.py` (Bloqueia Thread) -> Gera Áudio -> Toca + Texto no Terminal -> (Libera Thread).
