# 📂 Backend J.A.R.V.I.S. (Just A Rather Very Intelligent System)

Este diretório contém o motor lógico e a infraestrutura do assistente virtual. O projeto foi construído seguindo princípios de **Clean Architecture** e **Modularidade**, permitindo que a inteligência, os sentidos (áudio) e a memória operem de forma independente e integrada.

## 🎯 Objetivo do Projeto

O objetivo do J.A.R.V.I.S. é ser um assistente pessoal de **IA Local** de baixa latência. Ele prioriza a privacidade e a autonomia ao rodar modelos de linguagem (LLM) diretamente no hardware do usuário, oferecendo controle sobre o computador, persistência de memória e uma interface de voz natural.

---

## 🏗️ Organização do Sistema

O backend é dividido em três núcleos principais que se comunicam através do `main.py`:

### 1. `core/` (A Infraestrutura)

É o alicerce do sistema. Responsável por:

* **Configurações (`config.py`):** Gestão de variáveis de ambiente, caminhos e verificação de saúde do sistema.
* **Logs (`logger.py`):** Sistema de observabilidade que monitora eventos em tempo real no terminal e em arquivo.
* **Hardware (`SystemInfo.py`):** Sensores que permitem à IA saber o status de CPU, GPU e RAM.

### 2. `services/` (Os Sentidos e a Mente)

Contém a lógica de interação direta com o usuário:

* **`brain.py`:** O cérebro que utiliza o **Ollama** para processar intenções.
* **`listen.py`:** Transcrição de áudio para texto (STT) com sistema de *Wake Word*.
* **`speak.py`:** Síntese de voz (TTS) neural para uma resposta humanizada.

### 3. `database/` (A Memória)

Gerencia a persistência utilizando SQLite:

* **Memória Semântica:** Salva preferências (ex: nome do usuário).
* **Memória Episódica:** Mantém o histórico completo de interações para contexto futuro.

---

## ⚙️ O Arquivo `main.py` (O Orquestrador)

O `main.py` funciona como a **Unidade Central de Processamento** do software. Ele não executa a lógica de IA ou áudio diretamente, mas coordena como os módulos conversam entre si.

**Fluxo de Execução:**

1. **Boot:** Carrega as configurações do `core` e valida se as pastas e o banco de dados existem.
2. **Interface:** Inicia uma janela `pywebview` (Frontend) e estabelece uma ponte de comunicação entre Python e JavaScript.
3. **Loop Infinito (`jarvis_auto_loop`):**

* Aciona o `listen()` para capturar comandos.
* Registra a entrada do usuário no banco de dados.
* Envia o texto para o `brain.py` processar.
* Atualiza o estado visual da UI (Ouvindo/Processando/Falando).
* Aciona o `speak()` para dar o feedback sonoro.

4.**Shutdown:** Gerencia o encerramento seguro de threads e processos.

---

## 📦 O Arquivo `requirements.txt`

Este arquivo lista todas as dependências necessárias para que o ecossistema Python funcione. Sem ele, os módulos não conseguem importar as bibliotecas de terceiros.

| Categoria | Biblioteca Principal | Utilidade |
| --- | --- | --- |
| **IA/LLM** | `ollama` | Interface com o modelo Llama 3.1 local. |
| **Áudio** | `SpeechRecognition`, `edge-tts` | Conversão de fala em texto e vice-versa. |
| **Hardware** | `psutil`, `GPUtil` | Coleta de dados de telemetria do PC. |
| **Interface** | `pywebview` | Renderiza o frontend moderno sobre o código Python. |
| **Utilitários** | `python-dotenv`, `colorama` | Gestão de segredos e estilização do terminal. |

---

## 🚀 Como Executar

1. Certifique-se de ter o **Ollama** instalado e o modelo `llama3.1` baixado.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` na raiz (se necessário).
4. Inicie o sistema:

```bash
python main.py
```
