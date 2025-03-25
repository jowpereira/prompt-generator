import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Criando diretório de logs se não existir
os.makedirs("logs", exist_ok=True)

# Configuração do logger principal
logger = logging.getLogger("prompt_generator")
logger.setLevel(logging.DEBUG)

# Formatar as mensagens de log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Handler para console (stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Handler para arquivo
log_filename = f"logs/app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Adicionar handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def log_state(state: Dict[str, Any], prefix: str = "") -> None:
    """
    Registra o estado atual no log, removendo conteúdos muito longos.
    
    Args:
        state: Estado atual do processamento
        prefix: Prefixo opcional para a mensagem de log
    """
    try:
        # Criando uma cópia para não modificar o original
        state_copy = state.copy()
        
        # Remover ou truncar campos grandes para evitar logs excessivos
        for key in state_copy:
            if isinstance(state_copy[key], str) and len(state_copy[key]) > 500:
                state_copy[key] = f"{state_copy[key][:100]}... [truncado, total: {len(state_copy[key])} chars]"
            elif isinstance(state_copy[key], dict) and "output" in state_copy[key]:
                # Caso específico para saídas de formato
                outputs = {}
                for format_name, content in state_copy[key]["output"].items():
                    if isinstance(content, str) and len(content) > 500:
                        outputs[format_name] = f"{content[:100]}... [truncado, total: {len(content)} chars]"
                    else:
                        outputs[format_name] = content
                state_copy[key]["output"] = outputs
        
        # Registrar o estado no log
        message = f"{prefix}Estado atual: {json.dumps(state_copy, ensure_ascii=False, indent=2)}"
        logger.debug(message)
    except Exception as e:
        logger.warning(f"Erro ao registrar estado: {str(e)}")

def log_error(error: Exception, context: Optional[str] = None) -> None:
    """
    Registra um erro no log com contexto opcional.
    
    Args:
        error: Exceção a ser registrada
        context: Contexto adicional opcional
    """
    import traceback
    error_msg = f"Erro: {str(error)}"
    if context:
        error_msg = f"{context}: {error_msg}"
    
    logger.error(error_msg)
    logger.debug(f"Traceback: {traceback.format_exc()}")

def log_model_response(model_name: str, prompt: str, response: str) -> None:
    """
    Registra a interação com um modelo de linguagem.
    
    Args:
        model_name: Nome do modelo usado
        prompt: Prompt enviado ao modelo
        response: Resposta recebida do modelo
    """
    # Limitar o tamanho do prompt e resposta nos logs
    prompt_truncated = prompt if len(prompt) < 300 else f"{prompt[:300]}... [truncado]"
    response_truncated = response if len(response) < 500 else f"{response[:500]}... [truncado]"
    
    logger.debug(f"Modelo: {model_name}")
    logger.debug(f"Prompt: {prompt_truncated}")
    logger.debug(f"Resposta: {response_truncated}")

def log_format_output(format_name: str, content: str) -> None:
    """
    Registra a saída gerada para um formato específico.
    
    Args:
        format_name: Nome do formato (JSON, XML, Markdown)
        content: Conteúdo gerado
    """
    content_truncated = content if len(content) < 300 else f"{content[:300]}... [truncado]"
    logger.debug(f"Formato gerado - {format_name}:")
    logger.debug(content_truncated)

def get_log_filename() -> str:
    """
    Retorna o nome do arquivo de log atual.
    
    Returns:
        Caminho para o arquivo de log
    """
    return log_filename 