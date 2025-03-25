from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.models import PromptState
from src.logger import logger, log_state
import traceback

def plan_prompt(state: PromptState) -> Dict:
    """Gera um esqueleto estruturado para o prompt baseado nos requisitos coletados."""
    
    logger.info("Iniciando planejamento do prompt")
    
    try:
        # Verifica se os requisitos estão disponíveis
        if "requirements" not in state or not state["requirements"]:
            logger.error("Requisitos não fornecidos para planejamento")
            generic_draft = "Um prompt para atender às necessidades especificadas pelo usuário."
            return {"draft_prompt": generic_draft}
            
        logger.debug(f"Estado recebido no planejador: {state}")
        
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            logger.info("Modelo LLM inicializado para planejamento")
        except Exception as e:
            logger.error(f"Erro ao inicializar o modelo: {str(e)}")
            logger.error(traceback.format_exc())
            generic_draft = "Um prompt para atender às necessidades especificadas pelo usuário."
            return {"draft_prompt": generic_draft}
        
        template = """
        Como engenheiro de prompts experiente, crie um prompt COMPLETO e PRONTO PARA USO que atenda EXATAMENTE à solicitação original do usuário.
        
        Solicitação original do usuário: {user_input}
        
        Requisitos extraídos:
        - Objetivo: {objetivo}
        - Tom (se especificado): {tom}
        - Restrições: {restricoes}
        - Exemplos fornecidos: {exemplos}
        
        INSTRUÇÕES CRÍTICAS:
        1. O prompt que você criar DEVE estar relacionado DIRETAMENTE ao tópico da solicitação original do usuário
        2. Não crie um prompt genérico ou sobre um tema diferente do solicitado
        3. Seja específico sobre o tipo de conteúdo solicitado (histórias, instruções, etc.)
        4. Observe qualquer tom, limite de palavras ou outras restrições específicas
        
        Siga estas práticas de engenharia de prompt:
        1. Seja claro e específico nas instruções
        2. Separe contexto das instruções
        3. Use linguagem direta e objetiva
        4. Inclua restrições explícitas
        5. Estruture o conteúdo de forma lógica
        
        IMPORTANTE: 
        - NÃO utilize placeholders ou marcadores como [inserir X aqui]
        - Crie um prompt COMPLETO e FINAL, que possa ser usado diretamente pelo usuário
        - Preencha com conteúdo real e específico para o objetivo solicitado
        - Não mencione que é um "esqueleto" ou "estrutura"
        
        Crie o prompt completo, sem formatar para nenhum formato específico ainda.
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        requirements = state["requirements"]
        logger.debug(f"Requisitos para planejamento: {requirements}")
        
        # Prepara valores seguros para o template
        tom = requirements.get("tom", "Não especificado")
        restricoes = str(requirements.get("restricoes", {}))
        exemplos = str(requirements.get("exemplos", []))
        objetivo = requirements.get("objetivo", "Indefinido")
        
        # Extrai a solicitação original do usuário para usar como contexto adicional
        solicitacao_original = state.get("user_input", "")
        logger.debug(f"Solicitação original do usuário: {solicitacao_original[:50]}...")
        
        logger.debug(f"Enviando solicitação para planejamento de prompt com objetivo: {objetivo[:50]}...")
        
        try:
            result = chain.invoke({
                "objetivo": objetivo,
                "tom": tom,
                "restricoes": restricoes,
                "exemplos": exemplos,
                "user_input": solicitacao_original  # Adiciona a entrada original do usuário
            })
            
            if not result or not result.content:
                logger.error("Resposta vazia do modelo")
                return {"draft_prompt": "Um prompt para atender o objetivo: " + objetivo}
                
            logger.info("Esqueleto do prompt gerado com sucesso")
            log_state({"draft_prompt": result.content[:100] + "..."}, "rascunho_prompt")
            
            return {"draft_prompt": result.content}
        except Exception as e:
            logger.error(f"Erro na chamada do modelo: {str(e)}")
            logger.error(traceback.format_exc())
            return {"draft_prompt": "Um prompt para atender o objetivo: " + objetivo}
        
    except Exception as e:
        logger.error(f"Erro no planejamento do prompt: {str(e)}")
        logger.error(traceback.format_exc())
        # Fallback para um esqueleto genérico
        generic_draft = "Um prompt básico para atingir o objetivo especificado."
        return {"draft_prompt": generic_draft} 