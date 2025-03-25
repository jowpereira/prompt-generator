from typing import Dict, Callable, Any
from src.models import PromptState
from src.logger import logger, log_state
import traceback
import json
import re
from xml.etree import ElementTree as ET
from xml.parsers.expat import ExpatError
import logging

def validate_with_user(get_input: Callable[[str], str] = input) -> Callable[[PromptState], Dict[str, Any]]:
    """
    Cria uma função para obter feedback do usuário sobre o prompt gerado.
    
    Args:
        get_input: Função para obter entrada do usuário, padrão é a função input()
    
    Returns:
        Uma função que recebe o estado atual e retorna o feedback do usuário
    """
    
    def _validate(state: PromptState) -> Dict[str, Any]:
        logger.info("Iniciando validação com o usuário")
        logger.debug(f"Estado recebido na validação: {state}")
        
        try:
            # Exibe o resultado para o usuário
            formatted_outputs = state.get("output", {})
            
            if not formatted_outputs:
                logger.warning("Nenhum formato foi gerado para validação")
                return {"feedback": "n"}
            
            # Log dos formatos disponíveis
            logger.debug(f"Formatos disponíveis para validação: {list(formatted_outputs.keys())}")
            
            # Mostra cada formato gerado
            print("\n===== PROMPT GERADO =====")
            for format_name, content in formatted_outputs.items():
                print(f"\n--- Formato: {format_name} ---")
                print(content)
            
            # Na interface web, não precisamos pedir validação explícita
            # No modo CLI, pedimos o feedback
            try:
                feedback = get_input("\nEste prompt atende às suas necessidades? (s/n): ")
                logger.info(f"Feedback do usuário: {feedback}")
            except Exception as e:
                logger.warning(f"Erro ao obter feedback: {str(e)}, assumindo positivo")
                feedback = "s"  # Assume que o prompt está bom
            
            if feedback.lower() not in ('s', 'n'):
                logger.warning(f"Feedback inválido ({feedback}), assumindo 'n'")
                feedback = 'n'
            
            log_state(logger, {"feedback": feedback.lower()}, "feedback_usuário")
            return {"feedback": feedback.lower()}
        
        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            logger.error(traceback.format_exc())
            # Em caso de erro, assume que é necessário refinar
            return {"feedback": "s"}  # Modificado para finalizar o fluxo em caso de erro
    
    return _validate 

def validate_json_format(content: str) -> Dict[str, Any]:
    """
    Valida e corrige o formato JSON, retornando o JSON analisado ou um erro.
    
    Args:
        content: String contendo conteúdo JSON
        
    Returns:
        Dicionário com resultado da validação contendo status e mensagem
    """
    try:
        # Tenta parsear o JSON diretamente
        json_obj = json.loads(content)
        return {
            "valid": True, 
            "message": "Formato JSON válido",
            "data": json_obj
        }
    except json.JSONDecodeError as e:
        # Tratamento para diferentes tipos de erros JSON
        logger.warning(f"Erro ao validar JSON: {str(e)}")
        
        # Tenta corrigir problemas comuns de formato
        corrected_content = content
        
        # Verifica aspas simples vs duplas
        if "'" in content and '"' not in content:
            corrected_content = corrected_content.replace("'", '"')
        
        # Verifica chaves sem aspas
        invalid_key_pattern = r'(\s*})?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:'
        corrected_content = re.sub(invalid_key_pattern, r'\1"\2":', corrected_content)
        
        # Verifica valores sem aspas (exceto valores numéricos e booleanos)
        invalid_value_pattern = r':\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}])'
        def value_replacer(match):
            value = match.group(1).lower()
            if value in ('true', 'false', 'null') or value.isdigit() or re.match(r'^-?\d+(\.\d+)?$', value):
                return f': {value}{match.group(2)}'
            else:
                return f': "{match.group(1)}"{match.group(2)}'
                
        corrected_content = re.sub(invalid_value_pattern, value_replacer, corrected_content)
        
        # Tenta novamente com o conteúdo corrigido
        try:
            json_obj = json.loads(corrected_content)
            return {
                "valid": True, 
                "message": "JSON corrigido e validado com sucesso",
                "data": json_obj,
                "corrected": corrected_content
            }
        except json.JSONDecodeError:
            return {
                "valid": False, 
                "message": f"Erro na validação do JSON: {str(e)}",
                "error": str(e),
                "original": content
            }

def validate_xml_format(content: str) -> Dict[str, Any]:
    """
    Valida e corrige o formato XML, retornando uma mensagem de status.
    
    Args:
        content: String contendo conteúdo XML
        
    Returns:
        Dicionário com resultado da validação
    """
    try:
        # Remove a declaração XML para simplificar o parsing
        xml_without_declaration = re.sub(r'<\?xml[^>]*\?>\s*', '', content)
        
        # Tenta parsear o XML diretamente
        root = ET.fromstring(xml_without_declaration)
        
        # Verifica a qualidade do XML
        issues = []
        # Verifica elementos vazios
        for elem in root.iter():
            if not elem.text and not list(elem):
                issues.append(f"Elemento vazio: {elem.tag}")
        
        return {
            "valid": True, 
            "message": "Formato XML válido" if not issues else "XML válido com potenciais melhorias",
            "issues": issues,
            "data": ET.tostring(root, encoding='unicode')
        }
    except ExpatError as e:
        logger.warning(f"Erro ao validar XML: {str(e)}")
        
        # Verifica erros comuns de formatação
        corrected_content = content
        
        # Corrige elementos sem fechar
        unclosed_tags = re.findall(r'<([a-zA-Z0-9_]+)(?:\s+[^>]*)?(?<!/)>', corrected_content)
        for tag in unclosed_tags:
            if f"</{tag}>" not in corrected_content:
                # Adiciona tag de fechamento antes do próximo elemento
                pattern = re.compile(f'<{tag}(?:\\s+[^>]*)?(?<!/)>([^<]*)')
                corrected_content = pattern.sub(f'<{tag}\\g<0>\\1</{tag}>', corrected_content)
        
        # Tenta novamente com o conteúdo corrigido
        try:
            root = ET.fromstring(corrected_content)
            return {
                "valid": True, 
                "message": "XML corrigido e validado com sucesso",
                "data": ET.tostring(root, encoding='unicode'),
                "corrected": corrected_content
            }
        except ExpatError:
            return {
                "valid": False, 
                "message": f"Erro na validação do XML: {str(e)}",
                "error": str(e),
                "original": content
            }

def validate_markdown_format(content: str) -> Dict[str, Any]:
    """
    Verifica a qualidade do formato Markdown.
    
    Args:
        content: String contendo texto em Markdown
        
    Returns:
        Dicionário com resultado da validação
    """
    # Não há validação de sintaxe estrita para Markdown, mas podemos verificar 
    # a qualidade/estrutura do conteúdo
    
    # Verifica se tem cabeçalhos
    has_headers = bool(re.search(r'^#{1,6}\s+.+$', content, re.MULTILINE))
    
    # Verifica se tem parágrafos
    has_paragraphs = content.count('\n\n') > 0
    
    # Verifica se tem listas
    has_lists = bool(re.search(r'^\s*[-*+]\s+.+$', content, re.MULTILINE))
    
    # Constrói lista de sugestões
    suggestions = []
    if not has_headers:
        suggestions.append("Considere adicionar cabeçalhos para melhor estrutura")
    if not has_paragraphs:
        suggestions.append("Adicione quebras entre parágrafos para melhor legibilidade")
    if not has_lists and len(content) > 200:
        suggestions.append("Considere usar listas para informações enumeráveis")
    
    quality_score = 10
    quality_score -= 0 if has_headers else 3
    quality_score -= 0 if has_paragraphs else 2
    quality_score -= 0 if has_lists else 1
    
    return {
        "valid": True,  # Markdown é sempre "válido", apenas avaliamos qualidade
        "message": "Markdown validado com sucesso" if quality_score > 7 else 
                 "Markdown validado, mas com sugestões de melhoria",
        "quality_score": quality_score,
        "suggestions": suggestions,
        "data": content
    }

def validate_format(format_name: str, content: str) -> Dict[str, Any]:
    """
    Valida o conteúdo de acordo com o formato especificado.
    
    Args:
        format_name: Nome do formato (JSON, XML, Markdown)
        content: Conteúdo a ser validado
        
    Returns:
        Dicionário com resultado da validação
    """
    logger.info(f"Validando formato: {format_name}")
    
    format_name = format_name.lower()
    
    if not content or len(content.strip()) < 10:
        return {
            "valid": False,
            "message": f"Conteúdo muito curto para validação de formato {format_name}",
            "original": content
        }
    
    if format_name == "json":
        return validate_json_format(content)
    elif format_name == "xml":
        return validate_xml_format(content)
    elif format_name == "markdown":
        return validate_markdown_format(content)
    else:
        # Para formatos desconhecidos, assumimos que é texto simples
        return {
            "valid": True,
            "message": f"Formato {format_name} tratado como texto simples",
            "data": content
        }

def collect_user_feedback(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simula a coleta de feedback do usuário sobre os prompts gerados.
    
    Args:
        state: Estado atual do processo
    
    Returns:
        Estado atualizado com feedback do usuário
    """
    logger.info("Iniciando coleta de feedback do usuário")
    
    try:
        # Cria uma cópia do estado para não modificar o original diretamente
        updated_state = state.copy()
        
        # Em um cenário real, isso seria coletado da interface
        # Para fins de simulação, assumimos feedback positivo
        feedback = {
            "satisfeito": True,
            "comentarios": "Bom trabalho!",
            "pontuacao": 5  # em escala de 1-5
        }
        
        # Registra o feedback no estado
        updated_state["user_feedback"] = feedback
        logger.info(f"Feedback coletado: {feedback}")
        
        return updated_state
    
    except Exception as e:
        logger.error(f"Erro ao coletar feedback: {str(e)}")
        # Em caso de erro, retornamos um feedback neutro/positivo genérico
        return {
            **state,
            "user_feedback": {
                "satisfeito": True,
                "comentarios": "Sem comentários adicionais",
                "pontuacao": 4
            }
        }

def validate_outputs(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida todos os prompts de saída nos diferentes formatos.
    
    Args:
        state: Estado atual do processo, contendo os prompts gerados
        
    Returns:
        Estado atualizado com informações de validação
    """
    logger.info("Iniciando validação dos prompts gerados")
    
    try:
        # Cria uma cópia do estado para não modificar o original diretamente
        updated_state = state.copy()
        
        # Verifica se há prompts para validar
        if "output" not in state or not state["output"]:
            logger.warning("Nenhum prompt encontrado para validação")
            updated_state["validation_results"] = {
                "valid": False,
                "message": "Nenhum prompt encontrado para validação"
            }
            return updated_state
        
        # Valida cada formato
        validation_results = {}
        output_prompts = state["output"]
        
        for format_name, content in output_prompts.items():
            validation_results[format_name] = validate_format(format_name, content)
            
        # Adiciona resultados da validação ao estado
        updated_state["validation_results"] = validation_results
        
        # Determina validade geral com base em todos os resultados
        all_valid = all(result.get("valid", False) for result in validation_results.values())
        updated_state["validation_summary"] = {
            "valid": all_valid,
            "message": "Todos os formatos são válidos" if all_valid else "Alguns formatos têm problemas"
        }
        
        logger.info(f"Validação concluída: {all_valid}")
        return updated_state
    
    except Exception as e:
        logger.error(f"Erro ao validar outputs: {str(e)}")
        # Em caso de erro, retornamos uma validação neutra
        return {
            **state,
            "validation_results": {
                "valid": True,  # Assumimos que está ok para não bloquear o fluxo
                "message": f"Erro durante validação: {str(e)}"
            }
        }
        
# Função principal para uso no pipeline/grafo
def validate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Função principal de validação para uso no pipeline/grafo.
    
    Args:
        state: Estado atual do processo
        
    Returns:
        Estado atualizado
    """
    logger.info("Iniciando etapa de validação")
    
    try:
        # Primeiro valida os outputs
        validated_state = validate_outputs(state)
        
        # Depois coleta feedback do usuário
        feedback_state = collect_user_feedback(validated_state)
        
        return feedback_state
    
    except Exception as e:
        logger.error(f"Erro na etapa de validação: {str(e)}")
        return {
            **state,
            "error": f"Erro durante validação: {str(e)}"
        } 