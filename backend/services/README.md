# 🧠 Documentação do Módulo Services

Este diretório contém a lógica central do sistema J.A.R.V.I.S., dividida em três responsabilidades principais: **Input (Audição)**, **Processamento (Cérebro)** e **Output (Fala)**.

## 📂 Estrutura de Arquivos

| Arquivo | Função | Principais Bibliotecas |
| --- | --- | --- |
| **`brain.py`** | Controlador central, gerencia o fluxo de decisão e conecta-se à IA (Ollama). | `ollama`, `sys`, `os` |
| **`listen.py`** | Captura de áudio, detecção de *Wake Word* e transcrição (STT). | `speech_recognition`, `re` |
| **`speak.py`** | Síntese de voz (TTS) híbrida (Online/Offline) e reprodução de áudio. | `edge_tts`, `pygame`, `pyttsx3` |

---

## 1. `brain.py` (O Maestro)

O cérebro é responsável por orquestrar a interação. Ele inicia o loop principal, decide se o comando é uma função do sistema ou uma pergunta para a IA Generativa, e gerencia o histórico de conversa.

### Funcionalidades Chave:

* **System Prompt (Persona):** Define a personalidade do J.A.R.V.I.S. (Britânico, sarcástico, conciso) e impõe regras estritas de formatação (sem markdown, sem listas) para otimizar a síntese de voz.
* **Memória de Curto Prazo:** Mantém um histórico deslizante (`chat_history`) das últimas 6-10 interações para manter o contexto da conversa sem estourar a janela de contexto do modelo.
* **Roteador de Comandos (`execute_command`):**
* **Hardcoded:** Intercepta comandos críticos como "desligar" ou "reiniciar memória" antes de consultar a IA.
* **Generativo:** Envia o texto para o modelo local `llama3.1:8b` via Ollama.


* **Controle de Feedback:** Utiliza `ear_pause()` e `ear_resume()` para "tapar os ouvidos" enquanto fala, evitando que o J.A.R.V.I.S. ouça a si mesmo e entre em loop.

### Fluxo de Execução:

1. Inicializa e cumprimenta.
2. Entra em Loop Infinito `while True`.
3. Ouve (`listen()`) -> Processa (`execute_command()`) -> Fala (`speak()`).

---

## 2. `listen.py` (Os Ouvidos)

Responsável pela **transcrição de áudio para texto (STT)**. Utiliza a Google Speech Recognition API para alta precisão em Português-BR.

### Funcionalidades Chave:

* **Calibração de Ruído:** Ao iniciar, o sistema escuta o ambiente por 1 segundo para ajustar o limiar de ruído (`adjust_for_ambient_noise`).
* **Sistema de Wake Word (Palavra-chave):**
* Utiliza **Regex (`\bword\b`)** para detectar variações do nome (Jarvis, Jarbas, Javis) dentro de uma frase.
* Remove o nome da frase antes de processar o comando (Ex: "Jarvis que horas são" vira "que horas são").

* **Janela de Conversação (Active Mode):**
* Se o usuário falar o nome "Jarvis", um **Timer de 60 segundos** é ativado.
* Dentro dessa janela, não é necessário repetir o nome "Jarvis". O sistema aceita qualquer fala direta.
* Após 60s de inatividade, ele volta para o modo Standby (esperando o nome).

* **Filtros de Cancelamento:** Ignora comandos se detectar palavras como "esquece", "cancelar" ou "deixa quieto".

---

## 3. `speak.py` (A Voz)

Responsável pela **síntese de texto para áudio (TTS)**. Possui uma arquitetura híbrida robusta para garantir que o J.A.R.V.I.S. sempre consiga falar.

### Funcionalidades Chave:

* **Modo Online (Principal):**
* Utiliza a biblioteca **`edge_tts`** (motor neural da Microsoft Azure via Edge).
* Voz configurada: `pt-BR-AntonioNeural` (Voz masculina natural).
* Aceleração: `rate="+10%"` para maior fluidez.

* **Modo Offline (Backup):**
* Se a internet falhar ou o `edge_tts` der erro, ativa automaticamente o **`pyttsx3`** (voz robótica do sistema operacional).

* **Gerenciamento de Arquivos Dinâmicos:**
* Utiliza `uuid` para gerar nomes de arquivos de áudio temporários únicos (ex: `audio_a1b2...mp3`).
* Isso soluciona o erro de *PermissionError* do Windows, evitando conflito de arquivos em uso.
* O arquivo é deletado imediatamente após a reprodução.

* **Efeito Datilógrafo:**
* Uma Thread paralela exibe o texto no terminal letra por letra (`typewriter_effect`) sincronizado com o áudio.

* **Tratamento de Gírias:**
* A função `_treat_text` expande abreviações (vc -> você, tmj -> tamo junto) antes de enviar para a IA de voz, garantindo a pronúncia correta.

---

## ⚙️ Dependências do Sistema

Para que este módulo funcione, o ambiente Python deve ter:

```txt
ollama
SpeechRecognition
pyaudio (para microfone)
edge-tts
pygame
pyttsx3
python-dotenv

```

*Nota: É necessário ter o servidor **Ollama** rodando localmente com o modelo `llama3.1:8b` baixado.*