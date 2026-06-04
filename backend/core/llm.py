import os
from .config import settings
from .logger import log

os.environ["OLLAMA_HOST"] = settings.OLLAMA_HOST


def query_ollama(messages, format=None, temperature=0.7):
    """Centraliza chamadas ao Ollama para tratamento de erro e config."""
    try:
        from ollama import Client
        host = settings.OLLAMA_HOST
        if not host.startswith("http"):
            host = f"http://{host}"
        client = Client(host=host, timeout=120)
        response = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            format=format,
            options={'temperature': temperature}
        )
        return response['message']['content']
    except Exception as e:
        log.error(f"Erro na comunicação com Ollama: {e}")
        return None


def query_ollama_stream(messages, temperature=0.7):
    """Centraliza chamadas streaming ao Ollama."""
    try:
        from ollama import Client
        host = settings.OLLAMA_HOST
        if not host.startswith("http"):
            host = f"http://{host}"
        client = Client(host=host, timeout=120)
        response = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            options={'temperature': temperature},
            stream=True
        )
        for chunk in response:
            yield chunk['message']['content']
    except Exception as e:
        log.error(f"Erro na comunicação streaming com Ollama: {e}")
        yield "Erro de processamento neural."
