# 📘 Guia de Desenvolvimento de Skills (J.A.R.V.I.S.)

Este documento serve como manual técnico para expandir as capacidades do J.A.R.V.I.S.
Uma **Skill** é um módulo autônomo que permite à IA realizar uma ação concreta no sistema operacional ou na web (ex: abrir programas, controlar volume, buscar no Google).

---

## 🏗️ Arquitetura de Uma Skill

Para adicionar um novo "poder" ao J.A.R.V.I.S., você deve seguir um fluxo de 3 etapas:

1. **Criação (The Body):** Escrever o script Python que executa a ação.
2. **Educação (The Mind):** Ensinar o Roteador de Intenção (`brain.py`) a reconhecer esse novo pedido.
3. **Integração (The Nervous System):** Conectar a decisão da IA à execução do script.

---

## 📂 Passo 1: Criando o Arquivo da Skill

**Exemplo Prático: Skill de Abrir Programas (`app_launcher.py`)**

Crie o arquivo `backend/skills/app_launcher.py`:

```python
import os
import subprocess
from core.logger import log

def open_program(program_name):
    """
    Tenta abrir um programa baseado no nome.
    Retorna uma tupla: (Sucesso: bool, Mensagem: str)
    """
    log.info(f"🚀 [SKILL] Tentando abrir: {program_name}")
    
    # Dicionário de Mapeamento (Nome Falado -> Comando Real)
    apps = {
        "spotify": "spotify",
        "navegador": "chrome",
        "chrome": "chrome",
        "visual studio": "code",
        "vs code": "code",
        "bloco de notas": "notepad",
        "calculadora": "calc"
    }
    
    # Normaliza o nome para busca
    target = program_name.lower().strip()
    cmd = apps.get(target)
    
    if not cmd:
        return False, f"Desculpe, não sei como abrir o '{program_name}' ainda."
        
    try:
        # Popen é melhor que os.system pois não trava o script
        subprocess.Popen(cmd, shell=True) 
        return True, f"Iniciando {target}."
    except Exception as e:
        log.error(f"Erro ao abrir {target}: {e}")
        return False, f"Houve um erro técnico ao tentar abrir o {target}."

```

---

## 🧠 Passo 2: Ensinar o Cérebro (`brain.py`)

Você precisa atualizar o **Roteador de Intenção** para que a IA saiba que agora ela tem essa capacidade.

Vá até a função `classify_intent` no arquivo `brain.py`:

### A. Atualize o Schema JSON

Adicione um campo `entity` (entidade/alvo) para que a IA extraia **O QUE** você quer abrir.

*Antes:*

```python
schema = """{ "intent": "...", "confidence": float }"""

```

*Depois (Com suporte a Entidades):*

```python
schema = """
{
    "intent": "SHUTDOWN" | "HARDWARE" | "OPEN_APP" | ... ,
    "entity": "string (o objeto da ação, ex: 'spotify', 'luz da sala') ou null",
    "confidence": float
}
"""

```

### B. Atualize o Prompt de Categorias

Adicione a nova categoria na lista explicativa dentro da variável `prompt`:

```python
    CATEGORIAS:
    - SHUTDOWN: ...
    - HARDWARE: ...
    # --- ADICIONE ISTO ---
    - OPEN_APP: O usuário quer abrir um software, site ou aplicativo. (Ex: "Abra o Spotify", "Inicie o VS Code"). O campo 'entity' deve conter o nome do app.
    # ---------------------
    - CHAT: ...

```

---

## 🔌 Passo 3: Integração (`brain.py`)

Agora, conecte a intenção detectada à função que você criou no Passo 1.

### A. Importe a Skill

No topo do `brain.py`:

```python
from skills.app_launcher import open_program

```

### B. Atualize o `execute_command`

Adicione a lógica no bloco de decisão:

```python
def execute_command(command):
    decision = classify_intent(command)
    intent = decision.get("intent")
    entity = decision.get("entity") # <--- Captura o alvo (ex: "spotify")
    
    # ... (outros ifs) ...

    # --- NOVA SKILL ---
    elif intent == "OPEN_APP":
        if entity:
            speak(f"Abrindo {entity}...")
            success, msg = open_program(entity)
            return msg # O JARVIS fala o resultado (ex: "Iniciando spotify")
        else:
            return "Entendi que você quer abrir algo, mas não identifiquei o quê."

    # ... (else final) ...

```

---

## ✅ Resumo do Checklist

Para cada nova Skill, verifique:

1. [ ] O arquivo `.py` existe na pasta `skills/`?
2. [ ] A função retorna uma resposta clara (texto) para o JARVIS falar?
3. [ ] A categoria foi adicionada ao Prompt no `classify_intent`?
4. [ ] O campo `entity` está sendo extraído corretamente pelo JSON?
5. [ ] O `import` foi feito no `brain.py`?
6. [ ] O `elif` correspondente foi criado no `execute_command`?

---

## 💡 Dica de Engenharia

Para skills complexas (como automação web com Selenium), sempre use **Threads** ou **Subprocessos** na sua função de skill. Se a skill demorar 10 segundos para rodar e travar o `brain.py`, o JARVIS ficará "surdo" durante esse tempo.
