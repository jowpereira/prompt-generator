from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.models import UserRequirements, PromptState
from typing import Dict
from src.logger import logger, log_state
import traceback
import json

def collect_requirements(state: PromptState) -> Dict:
    """Coleta e valida os requisitos do usuário para geração do prompt."""
    
    logger.info("Iniciando coleta de requisitos")
    
    try:
        # Verifica se user_input está disponível
        if "user_input" not in state:
            logger.error("Estado sem 'user_input'. Estado recebido: " + str(state))
            default_requirements = {"objetivo": "Indefinido", "formato": ["Markdown"]}
            return {"requirements": default_requirements, "formats": ["Markdown"]}
            
        logger.info(f"Entrada do usuário: {state['user_input']}")
        
        # Extrai formato diretamente da entrada do usuário para caso de falha da IA
        formatos = ["Markdown"]  # Formato padrão
        entrada = state['user_input'].lower()
        
        # Detecção mais robusta de formatos
        if "formato json" in entrada or " json" in entrada or "\njson" in entrada:
            formatos = ["JSON"]
        elif "formato xml" in entrada or " xml" in entrada or "\nxml" in entrada:
            formatos = ["XML"]
        elif "formato markdown" in entrada or " markdown" in entrada or "\nmarkdown" in entrada:
            formatos = ["Markdown"]
            
        logger.info(f"Formatos detectados diretamente da entrada: {formatos}")
        
        # Extrai objetivo básico como fallback
        objetivo_base = "Geração de prompt conforme solicitado pelo usuário"
        
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            logger.info("Modelo LLM inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar o modelo: {str(e)}")
            logger.error(traceback.format_exc())
            default_requirements = {"objetivo": objetivo_base, "formato": formatos}
            log_state(default_requirements, "requisitos_padrão_após_erro_chamada")
            return {"requirements": default_requirements, "formats": formatos}
        
        template = """
        Como assistente especializado em engenharia de prompts, vou analisar a entrada do usuário
        e extrair requisitos estruturados para criação de um prompt eficaz.
        
        Entrada do usuário: {user_input}
        
        Extraia TODOS os detalhes específicos da entrada, sem adicionar suposições genéricas.
        IMPORTANTE: Extraia o objetivo EXATO mencionado pelo usuário, sem generalizar.
        
        Estruture as seguintes informações em um objeto JSON válido:
        {{
            "objetivo": "Extraia o objetivo ESPECÍFICO mencionado pelo usuário, com todos os detalhes",
            "formato": ["Lista de formatos específicos mencionados: Markdown, JSON, XML"],
            "tom": "Tom de comunicação específico mencionado pelo usuário",
            "restricoes": {{"Restrições específicas mencionadas pelo usuário"}},
            "exemplos": ["Exemplos específicos fornecidos pelo usuário"]
        }}
        
        Se algum campo não for especificado pelo usuário, inclua-o no JSON com valor vazio ou apropriado, 
        mas NÃO adicione informações genéricas que não estejam na entrada original.
        
        Retorne apenas o objeto JSON válido, sem texto adicional.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        logger.debug(f"Enviando solicitação para extrair requisitos de: {state['user_input'][:50]}...")
        
        try:
            result = chain.invoke({"user_input": state["user_input"]})
            logger.debug(f"Resposta recebida: {result.content[:100]}...")
        except Exception as e:
            logger.error(f"Erro na chamada do modelo: {str(e)}")
            logger.error(traceback.format_exc())
            default_requirements = {"objetivo": objetivo_base, "formato": formatos}
            log_state(default_requirements, "requisitos_padrão_após_erro_chamada")
            return {"requirements": default_requirements, "formats": formatos}
        
        # Processamento e validação básica
        try:
            # Limpa possíveis caracteres extras
            content = result.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "", 1)
            if content.endswith("```"):
                content = content.replace("```", "", 1)
                
            content = content.strip()
            logger.debug(f"Conteúdo JSON a ser processado: {content[:100]}...")
            
            try:
                requirements = json.loads(content)
            except json.JSONDecodeError as e:
                # Tenta corrigir problemas comuns em JSON
                logger.warning(f"Erro ao decodificar JSON: {str(e)}. Tentando corrigir manualmente.")
                
                # Correção para o problema de restrições sem delimitador :
                if '"restricoes": {' in content and '"exemplos"' in content:
                    # Extrai o valor entre "restricoes": { e }, e adiciona aspas
                    import re
                    restricoes_match = re.search(r'"restricoes":\s*{\s*([^{}]+?)\s*}', content)
                    if restricoes_match:
                        restricao = restricoes_match.group(1).strip()
                        if not ':' in restricao:
                            # Adiciona formato de par chave-valor
                            nuevo_restricoes = f'"restricoes": {{"value": "{restricao}"}}'
                            content = re.sub(r'"restricoes":\s*{\s*[^{}]+?\s*}', nuevo_restricoes, content)
                            logger.debug(f"JSON corrigido: {content[:100]}...")
                
                # Tenta novamente com o JSON corrigido
                requirements = json.loads(content)
            
            logger.debug(f"JSON carregado com sucesso: {requirements}")
            
            # Validação mínima
            if "objetivo" not in requirements or not requirements.get("objetivo"):
                logger.warning("Objetivo não fornecido, usando valor da entrada direta")
                requirements["objetivo"] = objetivo_base
                
            # Sempre use os formatos detectados diretamente da entrada
            # Mesmo se o modelo retornar formatos, priorize os detectados diretamente
            requirements["formato"] = formatos
            logger.info(f"Formatos definidos como: {formatos}")
                
            # Garante que formato seja uma lista
            if isinstance(requirements.get("formato"), str):
                requirements["formato"] = [requirements["formato"]]
                
            logger.info(f"Requisitos coletados com sucesso: formato(s)={requirements['formato']}")
            log_state(requirements, "requisitos_coletados")
            
            return {"requirements": requirements, "formats": requirements["formato"]}
            
        except (json.JSONDecodeError, ValueError) as e:
            # Em caso de erro, prepara para pedir mais informações
            logger.error(f"Erro ao processar resposta do modelo: {str(e)}")
            logger.error(f"Conteúdo da resposta: {result.content}")
            logger.info("Usando valores padrão para os requisitos")
            default_requirements = {"objetivo": objetivo_base, "formato": formatos}
            log_state(default_requirements, "requisitos_padrão")
            return {"requirements": default_requirements, "formats": formatos}
    
    except Exception as e:
        logger.error(f"Erro na coleta de requisitos: {str(e)}")
        logger.error(traceback.format_exc())
        default_requirements = {"objetivo": "Indefinido", "formato": ["Markdown"]}
        return {"requirements": default_requirements, "formats": ["Markdown"]} 