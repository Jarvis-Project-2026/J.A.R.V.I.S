# 🤖 J.A.R.V.I.S. - Assistente Virtual Modular

Este projeto é um assistente virtual robusto desenvolvido com foco em **IA Local**, automação e uma arquitetura limpa (*Clean Architecture*). O sistema é dividido em módulos, sendo o diretório `backend/core/` o coração da infraestrutura.

## 📂 Estrutura do Núcleo (`core/`)

A camada `core` é responsável pela infraestrutura base, garantindo que o sistema seja resiliente, rastreável e capaz de persistir informações.

### 1. `config.py` - O Centro de Comando

Este arquivo gerencia todas as variáveis globais, caminhos de diretórios e configurações de ambiente do projeto.

* **Funcionamento:** Utiliza a biblioteca `pathlib` para garantir que o projeto funcione em qualquer sistema operacional (Windows/Linux) e `dotenv` para carregar segredos e preferências do arquivo `.env`.
* **Recursos:** * Criação automática de pastas necessárias (`logs`, `database`, `sounds`).
* Verificação de integridade (*Sanity Check*) ao iniciar.
* Definição de timeouts e modelos de IA (Ollama).

### 2. `logger.py` - O Escriba (Observabilidade)

Substitui o uso de `print()` por um sistema de monitoramento profissional.

* **Funcionamento:** Implementado como um **Singleton** (garante uma única instância no sistema todo).
* **Saídas Duplas:**
* **Terminal:** Exibe mensagens coloridas com `colorama` (DEBUG em Ciano, INFO em Verde, ERROR em Vermelho).
* **Arquivo (`jarvis.log`):** Salva o histórico completo com data e hora para auditoria.

### 3. `database.py` - A Memória de Longo Prazo

Gerencia a persistência de dados através do SQLite nativo.

* **Funcionamento:** Abstrai a complexidade do SQL para métodos simples de Python.
* **Tabelas Principais:**
* `memory`: Armazena pares Chave-Valor (ex: nome do usuário, preferências).
* `history`: Registra cada interação entre o usuário e a IA para manter o contexto.

* **Recurso UPSERT:** Atualiza informações existentes automaticamente se a chave já existir.

### 4. `SystemInfo.py` - Os Sensores de Hardware

Fornece telemetria detalhada sobre o computador onde o JARVIS está rodando.

* **Funcionamento:** Utiliza as bibliotecas `psutil` e `GPUtil` para monitorar recursos em tempo real.
* **Capacidades:**
* Monitoramento de CPU (frequência, núcleos, uso).
* Uso de RAM e status de GPU (carga, temperatura).
* Velocidade de rede (Upload/Download) e status de bateria.
* Tempo de atividade (*Uptime*) do sistema.

### 5. `__init__.py` - O Filtro de Inicialização

Responsável por preparar o pacote `core` e limpar o ambiente.

* **Funcionamento:** Silencia logs desnecessários de bibliotecas externas (como `urllib3` e `httpx`) para manter o terminal focado apenas nas mensagens do JARVIS.
* **Exports:** Define o que fica disponível para o resto do sistema via `__all__`.

---

## 🚀 Como os arquivos trabalham juntos

1. O **`main.py`** importa as **`settings`** (`config.py`) para saber onde estão os arquivos.
2. O **`__init__.py`** entra em ação silenciando o ruído de bibliotecas externas.
3. O **`logger.py`** inicia os canais de comunicação visual e de arquivo.
4. O **`database.py`** verifica se as tabelas de memória estão prontas.
5. O **`SystemInfo.py`** fica disponível para que o assistente possa responder perguntas como "Como está o meu computador?".

---

## 🛠️ Tecnologias Principais

* **Python 3.10+**
* **SQLite3** (Persistência)
* **Colorama** (UI Terminal)
* **Psutil** (Hardware)
* **Pathlib** (Sistema de Arquivos)
