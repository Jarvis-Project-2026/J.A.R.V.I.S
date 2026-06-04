import os
import string
from core.logger import log

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

_prompt_cache = {}

def load_prompt(filename, **kwargs):
    """
    Carrega um arquivo de prompt .md e aplica injeção de variáveis via Template se houver kwargs.
    Usa um cache em memória para evitar IO excessivo no disco.
    
    A sintaxe no arquivo .md deve ser $variavel.
    """
    filepath = os.path.join(PROMPTS_DIR, filename)
    
    if filepath not in _prompt_cache:
        if not os.path.exists(filepath):
            log.error(f"Erro: Arquivo de prompt não encontrado: {filepath}")
            return ""
            
        with open(filepath, 'r', encoding='utf-8') as f:
            _prompt_cache[filepath] = f.read()
            
    content = _prompt_cache[filepath]
    
    if kwargs:
        template = string.Template(content)
        # safe_substitute ignora variáveis no .md que não foram passadas no kwargs sem crashar
        return template.safe_substitute(**kwargs)
        
    return content
