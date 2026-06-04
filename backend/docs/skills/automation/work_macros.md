# ⚙️ Skill: work_macros.py

A skill `work_macros.py` pertence à categoria **Automation** e atua como o regente supremo da máquina. Ela aciona sequências orquestradas complexas chamadas de "Cenas", preparando o ambiente de trabalho, o layout de telas e o comportamento acústico do Windows simultaneamente com apenas uma ordem vocal.

## 📝 Contrato

- **INTENT**: `WORK_MACRO`
- **PROMPT_TEXT**: Carregada no cérebro central para interceptar pedidos de mutação ambiental (Ex: "Ativar modo desenvolvedor", "Preciso focar e estudar", "Sextou, liga o modo gamer").

---

## ⚙️ Arquitetura e Engenharia Interna

### 1. O Sub-Agente Semântico (`_ask_ollama_macro_expert`)

O cérebro dedica um agente terceirizado (`requests.post(Ollama)`) para converter divagações do usuário em chaves dicionariais estritas.

- O `MACRO_DECISION_PROMPT` restringe o pensamento da LLM a apenas devolver 4 valores permitidos no JSON final: `code`, `estudo`, `gamer` ou `outro`.
- Se o usuário falar *"Jarvis, bora trabalhar, abre minhas paradas de dev"*, a LLM formata para `{"mode": "code"}`.

### 2. Feedback de Imersão Assíncrono (Tony Stark Effect)

Cenas demoram para carregar porque exigem a leitura de discos rígidos abrindo múltiplos apps simultaneamente. Se a skill processasse tudo para só depois responder no `return`, o J.A.R.V.I.S. ficaria mudo por 10 segundos, quebrando a UX.

- O desenvolvedor consertou isso fazendo um *Late Import* (`from services.speak import speak`) e invocando `speak("Carregando protocolo...")` **antes** do loop `for app in scene["apps"]:` começar. Isso passa a incrível sensação de que o Jarvis está realmente trabalhando em *background* enquanto conversa com você.

### 3. Acoplamento de Skills Cruzadas (Cross-Skill Invocation)

Em vez de reinventar a roda ou copiar códigos de abertura de software, a `work_macros.py` injeta no núcleo a habilidade de acessar a tabela de memória do orquestrador central.

- Ela usa `from core import manager` e verifica dinamicamente se a skill `APP_CONTROL` está carregada na memória (`manager.skills["APP_CONTROL"]`).
- Em caso positivo, ela parasita a função `.execute()` do app_control, delegando para ela a dor de cabeça matemática de achar o executável, aplicar Fuzzy Match e abrir o app.

### 4. Bypasses de Automação Avançados

- **Silenciamento de SO (RegEdit)**: Quando no modo "Estudo", a skill não apenas fecha apps. Ela roda um script furtivo em `PowerShell` e sobrescreve a chave de *Registry* do Windows `NOC_GLOBAL_SETTING_TOASTS_ENABLED`. Isso silencia brutalmente todas as notificações e sons de aviso do Windows, ativando um *Do Not Disturb* absoluto.
- **Autoplay do Spotify via Hardware**: A API gratuita do Spotify bloqueia o comando `:play` externo. A skill realiza um bypass formidável:
  1. Injeta o protocolo URI nativo para obrigar o Windows a focar o Spotify (`start spotify:playlist:URI`).
  2. Dorme por 3 segundos para que a UI do Spotify carregue as músicas.
  3. Mapeia as C-Types do teclado (`ctypes.windll.user32.MapVirtualKeyA`) usando a *Scan Code* secreta `VK_MEDIA_PLAY_PAUSE (0xB3)`. O Python sinaliza ao Kernel do Windows que um humano apertou fisicamente o botão de Play/Pause em um Teclado Gamer Multimídia, forçando a música a tocar sem restrições de licença.

### 5. Tiling Manager Customizado (C# dentro do Python)

O Windows não tem sistemas nativos de Tiling (como o i3wm ou BSPWM no Linux). A skill `work_macros.py` constrói o seu próprio Tiling Manager "On-the-Fly".

- A função `organize_windows` cria uma string contendo código compilável de linguagem **C#**.
- Ela executa um comando `powershell` com a diretiva `Add-Type`, pedindo pro compilador .NET do Windows compilar aquele C# em tempo real, obtendo acesso nativo hiper-rápido à DLL `User32.dll`.
- **Inteligência Espacial**: O script invoca `System.Windows.Forms.Screen::AllScreens` para contar os monitores de hardware.
  - **Single Monitor Layout**: O VSCode recebe matematicamente `70%` (`[math]::Floor($prim.Width * 0.70)`) dos pixels esquerdos, e o Navegador é ancorado nos `30%` restantes.
  - **Dual Monitor Layout**: O VSCode é puxado para o Monitor 1 e recebe um comando de Maximize (`ShowWindow(3)`), enquanto o Navegador de internet cruza o abismo e maximiza no Monitor 2, deixando o ambiente de código intocado em segundos.

---

## 🛠️ Manutenção e Boas Práticas (Developer Guide)

- **Handles Mortos (Janelas Eletron/Chromium)**: Preste extrema atenção à linha `$_.MainWindowHandle -ne 0` no PowerShell embutido. Ferramentas construídas com Electron (Discord, Spotify, VSCode) criam processos no Windows que *não possuem* janela física (`MainWindowHandle = 0`). Sem esse filtro restrito, o C# tentará dar um resize no processo em background do Chromium, causando falha geral no Tiling Manager.
- **Tempo de Aguardo no Tiling**: Há um comando vital de `time.sleep(3)` antes da chamada de `organize_windows()`. Se for reduzido, o C# será disparado na velocidade da luz *antes* de que o HD/SSD tenha tido tempo de abrir a janela do VSCode. O Tiling manager não achará o `MainWindowHandle` na RAM e o painel continuará bagunçado. Caso mude para um PC com HDD antigo, aumente para `time.sleep(7)`.
