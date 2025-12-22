# 🤖 J.A.R.V.I.S. - Backend Core Package

O diretório `backend/core/` é o coração da infraestrutura do J.A.R.V.I.S. Ele implementa o **Facade Pattern**, centralizando o acesso a todas as funcionalidades essenciais do sistema através de um único ponto de entrada.

## 📂 Estrutura do Pacote (`core/`)

A camada `core` gerenta a infraestrutura base, garantindo persistência, observabilidade e telemetria.

### 1. `__init__.py` - O Portal (Facade)

Agora atua como a interface pública do pacote. Você pode importar tudo o que precisa diretamente de `core`.

- **Uso:** `from core import settings, log, db, manager, SystemInfo, JarvisAPI`
- **Silenciamento:** Filtra logs irrelevantes de bibliotecas como `httpx` e `urllib3`.

### 2. `config.py` - Centro de Configuração

Gerencia variáveis de ambiente, caminhos globais e estados iniciais.

- **Recursos:** Criação automática de diretórios (`logs`, `db`, `sounds`) e verificação de sanidade do ambiente.

### 3. `logger.py` - Sistema de Log Profissional

Implementa um Logger Singleton com suporte a cores no terminal e persistência em arquivo.

- **Níveis:** DEBUG (Ciano), INFO (Verde), WARNING (Amarelo), ERROR/CRITICAL (Vermelho).

### 4. `database.py` - Persistência SQLite

Gerencia a memória de longo prazo e o histórico de interações.

- **Tabelas:** `memory` (fatos/preferências), `history` (contexto de chat) e `hardware` (specs da máquina).

### 5. `SystemInfo.py` - Telemetria de Hardware

Monitora o estado físico da máquina hospedeira em tempo real.

- **Monitoramento:** CPU, RAM, GPU (via GPUtil), Rede, Disco e Bateria.
- **Alertas:** Capaz de disparar callbacks proativos quando limites críticos são atingidos.

### 6. `skill_loader.py` - Carregamento Dinâmico

Varre o diretório `skills/` e carrega módulos que seguem o contrato de interface (INTENT + execute).

### 7. `bridge.py` - Ponte UI/Backend

Gerencia a comunicação bidirecional com a interface gráfica (PyWebView), expondo a API de telemetria e o controle do HUD.

---

## 🚀 Como Utilizar

Graças ao padrão Facade, as camadas superiores (`services`, `main`, `skills`) agora utilizam imports limpos:

```python
from core import settings, log, db
```

## 🛠️ Tecnologias

- **Python 3.10+**
- **SQLite3**
- **Psutil / GPUtil**
- **Colorama**
