from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.models import PromptState
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from src.logger import logger, log_state
import traceback
import html

def generate_prompt_formats(state: PromptState) -> Dict:
    """Renderiza o prompt nos formatos solicitados pelo usuário."""
    
    logger.info(f"Iniciando geração de formatos")
    
    try:
        # Verifica se as entradas necessárias estão presentes
        if "formats" not in state or not state["formats"]:
            logger.error("Formatos não especificados para geração")
            return {"output": {"Markdown": "**Prompt não especificado**"}}
            
        if "draft_prompt" not in state or not state.get("draft_prompt"):
            logger.error("Rascunho do prompt não encontrado")
            return {"output": {"Markdown": "**Rascunho do prompt não encontrado**"}}
            
        logger.info(f"Gerando formatos: {state['formats']}")
        logger.debug(f"Estado recebido no gerador: {state}")
        
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            logger.info("Modelo LLM inicializado para geração de formatos")
        except Exception as e:
            logger.error(f"Erro ao inicializar o modelo: {str(e)}")
            logger.error(traceback.format_exc())
            # Cria um formato básico de fallback
            return {"output": {format_type: state["draft_prompt"] for format_type in state["formats"]}}
        
        # Função auxiliar para validar XML
        def validate_xml(xml_str):
            try:
                ET.fromstring(xml_str)
                return True
            except ET.ParseError as e:
                logger.warning(f"XML inválido: {str(e)}")
                return False
        
        # Função auxiliar para validar JSON
        def validate_json(json_str):
            try:
                json.loads(json_str)
                return True
            except json.JSONDecodeError as e:
                logger.warning(f"JSON inválido: {str(e)}")
                return False
        
        # Gerador de formatos específicos
        def generate_format(draft, format_type):
            logger.debug(f"Gerando formato: {format_type}")
            
            # Templates específicos para cada formato
            if format_type.upper() == "JSON":
                template = """
                Converta o seguinte prompt para o formato JSON estruturado.
                
                Prompt a ser convertido:
                {draft}
                
                INSTRUÇÕES ESPECÍFICAS PARA JSON:
                1. Crie um JSON válido com os campos apropriados para o conteúdo
                2. Use uma estrutura como esta, mas adaptada ao conteúdo:
                ```json
                {{
                  "title": "Título do prompt",
                  "description": "Descrição principal",
                  "instructions": [
                    "Instrução 1",
                    "Instrução 2"
                  ],
                  "constraints": [
                    "Restrição 1", 
                    "Restrição 2"
                  ],
                  "examples": [
                    "Exemplo 1",
                    "Exemplo 2"
                  ]
                }}
                ```
                3. Certifique-se de que todos os campos representem fielmente o conteúdo do prompt
                4. Não use campos como "[insira X aqui]" - preencha com conteúdo real
                
                Retorne APENAS o JSON formatado, sem texto adicional, markdown ou bloco de código.
                """
            elif format_type.upper() == "XML":
                template = """
                Converta o seguinte prompt para o formato XML estruturado.
                
                Prompt a ser convertido:
                {draft}
                
                INSTRUÇÕES ESPECÍFICAS PARA XML:
                1. Crie um XML válido que represente corretamente o conteúdo
                2. Use uma estrutura como esta, mas adaptada ao conteúdo:
                ```xml
                <prompt>
                  <title>Título do prompt</title>
                  <description>Descrição principal</description>
                  <instructions>
                    <item>Instrução 1</item>
                    <item>Instrução 2</item>
                  </instructions>
                  <constraints>
                    <item>Restrição 1</item>
                    <item>Restrição 2</item>
                  </constraints>
                  <examples>
                    <item>Exemplo 1</item>
                    <item>Exemplo 2</item>
                  </examples>
                </prompt>
                ```
                3. Certifique-se de que o XML seja bem formado, com tags fechadas corretamente
                4. Escape caracteres especiais como &, <, > quando necessário
                5. Não use campos como "[insira X aqui]" - preencha com conteúdo real
                
                Retorne APENAS o XML formatado, sem texto adicional, markdown ou bloco de código.
                """
            else:
                template = """
                Converta o seguinte prompt para o formato {format_type}.
                Garanta que a sintaxe esteja correta e a estrutura seja válida.
                
                Prompt a ser convertido:
                {draft}
                
                Retorne APENAS o prompt formatado, sem explicações adicionais.
                """
            
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | llm
            
            try:
                result = chain.invoke({
                    "draft": draft,
                    "format_type": format_type
                })
                
                # Validação básica por formato
                content = result.content
                
                # Limpa os marcadores de código
                if content.startswith("```") and content.endswith("```"):
                    content = content[3:-3]
                elif content.startswith(f"```{format_type.lower()}") and content.endswith("```"):
                    content = content[len(f"```{format_type.lower()}"):-3]
                
                content = content.strip()
                
                if format_type.upper() == "JSON" and not validate_json(content):
                    # Fallback para JSON inválido
                    logger.warning(f"Formato JSON gerado é inválido, usando fallback")
                    fallback = {"prompt": draft, "error": "Formato JSON inválido"}
                    return json.dumps(fallback, ensure_ascii=False, indent=2)
                elif format_type.upper() == "XML" and not validate_xml(content):
                    # Tenta corrigir XML mal formatado
                    logger.warning(f"Formato XML gerado é inválido, tentando corrigir")
                    try:
                        # Tenta remover qualquer linha com '```' que possa ter ficado
                        content = '\n'.join([line for line in content.split('\n') if not line.strip().startswith('```')])
                        
                        # Verifica se o XML tem a tag raiz
                        if not content.strip().startswith('<'):
                            content = f"<prompt>\n  <content>{content}</content>\n</prompt>"
                        
                        # Valida novamente
                        if validate_xml(content):
                            logger.info("XML corrigido com sucesso")
                        else:
                            # Se ainda não for válido, usa fallback
                            logger.warning(f"Formato XML gerado é inválido, usando fallback")
                            # Escapa o conteúdo para XML
                            draft_escaped = html.escape(draft)
                            return f"<prompt><error>Formato XML inválido</error><content>{draft_escaped}</content></prompt>"
                    except Exception as e:
                        logger.error(f"Erro ao tentar corrigir XML: {str(e)}")
                        # Escapa o conteúdo para XML
                        draft_escaped = html.escape(draft)
                        return f"<prompt><error>Erro na correção de XML: {str(e)}</error><content>{draft_escaped}</content></prompt>"
                else:
                    logger.debug(f"Formato {format_type} gerado com sucesso")
                    return content
            except Exception as e:
                logger.error(f"Erro ao gerar formato {format_type}: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Gera fallback de acordo com o tipo
                if format_type.upper() == "JSON":
                    fallback = {"prompt": draft, "error": str(e)}
                    return json.dumps(fallback, ensure_ascii=False, indent=2)
                elif format_type.upper() == "XML":
                    return f"<prompt><error>{str(e)}</error><content>{draft}</content></prompt>"
                else:
                    return f"# Prompt\n\n{draft}\n\n*Erro: {str(e)}*"
        
        # Gera cada formato solicitado
        output_formats = {}
        for format_type in state["formats"]:
            output_formats[format_type] = generate_format(state["draft_prompt"], format_type)
        
        if not output_formats:
            logger.warning("Nenhum formato foi gerado")
            output_formats["Markdown"] = f"# Prompt\n\n{state['draft_prompt']}"
            
        logger.info(f"Formatos gerados com sucesso: {list(output_formats.keys())}")
        log_state({"output_formats": list(output_formats.keys())}, "formatos_gerados")
        
        return {"output": output_formats}
        
    except Exception as e:
        logger.error(f"Erro na geração de formatos: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback para formato básico
        draft = state.get("draft_prompt", "Prompt não disponível")
        return {"output": {"Markdown": f"**Prompt Gerado**\n\n{draft}"}} 