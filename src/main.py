from typing import Dict, Any, Literal, List
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
import traceback

from src.models import PromptState
from src.requirements_collector import collect_requirements
from src.prompt_planner import plan_prompt
from src.format_generator import generate_prompt_formats
from src.validation import validate_with_user
from src.logger import logger, log_state

def create_prompt_graph():
    """Cria o grafo de fluxo para o gerador de prompts."""
    
    logger.info("Criando grafo de estado linear para o gerador de prompts")
    
    # Configuração do grafo de estados
    graph = StateGraph(PromptState)
    
    # Adição dos nós ao grafo
    graph.add_node("collect", collect_requirements)
    graph.add_node("plan", plan_prompt)
    graph.add_node("generate", generate_prompt_formats)
    
    # Definição das transições lineares simples (sem loops)
    graph.add_edge("collect", "plan")
    graph.add_edge("plan", "generate")
    graph.add_edge("generate", END)
    
    # Definir nó inicial (entry point)
    graph.set_entry_point("collect")
    
    # Compilação do grafo
    logger.info("Grafo linear compilado com sucesso")
    return graph.compile()

def process_prompt_pipeline(user_input: str) -> Dict[str, Any]:
    """
    Executa o pipeline de processamento do prompt de forma sequencial.
    
    Esta função substitui o grafo em caso de falha e garante que cada etapa
    seja executada corretamente.
    """
    logger.info("Executando pipeline de processamento sequencial")
    
    try:
        # Estado inicial
        state = {"user_input": user_input}
        log_state(state, "pipeline_estado_inicial")
        
        # 1. Coleta de requisitos
        try:
            logger.info("Pipeline: Iniciando coleta de requisitos")
            req_result = collect_requirements(state)
            state.update(req_result)
            logger.info("Pipeline: Requisitos coletados com sucesso")
        except Exception as e:
            logger.error(f"Pipeline: Erro na coleta de requisitos: {str(e)}")
            logger.error(traceback.format_exc())
            # Valores padrão em caso de falha
            state["requirements"] = {"objetivo": "Gerar prompt conforme solicitado", "formato": ["Markdown"]}
            state["formats"] = ["Markdown"]
        
        # 2. Planejamento do prompt
        try:
            logger.info("Pipeline: Iniciando planejamento do prompt")
            plan_result = plan_prompt(state)
            state.update(plan_result)
            logger.info("Pipeline: Prompt planejado com sucesso")
        except Exception as e:
            logger.error(f"Pipeline: Erro no planejamento do prompt: {str(e)}")
            logger.error(traceback.format_exc())
            # Valores padrão em caso de falha
            state["draft_prompt"] = "Um prompt para atender às necessidades especificadas."
        
        # 3. Geração de formatos
        try:
            logger.info("Pipeline: Iniciando geração de formatos")
            formats_result = generate_prompt_formats(state)
            state.update(formats_result)
            logger.info("Pipeline: Formatos gerados com sucesso")
        except Exception as e:
            logger.error(f"Pipeline: Erro na geração de formatos: {str(e)}")
            logger.error(traceback.format_exc())
            # Valores padrão em caso de falha
            state["output"] = {"Markdown": f"# Prompt\n\n{state.get('draft_prompt', 'Sem conteúdo disponível')}"}
        
        # Verifica se a saída foi gerada
        if "output" not in state or not state["output"]:
            logger.warning("Pipeline: Nenhuma saída foi gerada, usando formato padrão")
            state["output"] = {"Markdown": f"# Prompt Padrão\n\n{state.get('draft_prompt', 'Conteúdo não disponível')}"}
        
        log_state(state, "pipeline_resultado_final")
        logger.info("Pipeline: Processamento concluído com sucesso")
        
        return state
    except Exception as e:
        logger.error(f"Pipeline: Erro crítico no pipeline: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Erro no processamento: {str(e)}",
            "output": {"Markdown": f"# Erro na Geração\n\nOcorreu um erro: {str(e)}"}
        }

def run_prompt_generator(user_input: str) -> Dict[str, Any]:
    """Executa o gerador de prompts com a entrada do usuário."""
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Verifica se a chave da API está definida
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        return {
            "error": "API Key não configurada. Crie um arquivo .env com sua OPENAI_API_KEY.",
            "output": {"Markdown": "# Erro de Configuração\n\nAPI Key não configurada. Crie um arquivo .env com sua OPENAI_API_KEY."}
        }
    
    logger.info(f"Iniciando geração de prompt com entrada: {user_input[:50]}...")
    
    try:
        # Tenta executar usando o grafo
        try:
            logger.info("Tentando executar usando o grafo de estados")
            app = create_prompt_graph()
            
            # Estado inicial
            initial_state = {"user_input": user_input}
            log_state(initial_state, "grafo_estado_inicial")
            
            # Executa o grafo
            logger.info("Iniciando execução do grafo")
            result = app.invoke(initial_state)
            
            # Verifica se o resultado foi gerado corretamente
            if "output" in result and result["output"]:
                logger.info("Grafo executado com sucesso")
                log_state(result, "grafo_resultado_final")
                return result
            else:
                logger.warning("Grafo executado mas sem saída gerada, executando pipeline alternativo")
                return process_prompt_pipeline(user_input)
                
        except Exception as e:
            logger.error(f"Erro na execução do grafo: {str(e)}")
            logger.error(traceback.format_exc())
            logger.info("Executando pipeline alternativo devido a falha no grafo")
            return process_prompt_pipeline(user_input)
            
    except Exception as e:
        logger.error(f"Erro crítico no gerador de prompts: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Erro ao gerar o prompt: {str(e)}",
            "output": {"Markdown": f"# Erro na Geração\n\nOcorreu um erro fatal: {str(e)}"}
        }

if __name__ == "__main__":
    print("="*50)
    print("GERADOR DE PROMPTS")
    print("="*50)
    
    user_input = input("\nDescreva o prompt que você deseja gerar: ")
    
    try:
        result = run_prompt_generator(user_input)
        
        # Exibe resultados
        if "output" in result and result["output"]:
            print("\n\nProcesso finalizado!")
            print("Abaixo estão os prompts gerados nos formatos solicitados:")
            
            for format_name, content in result.get("output", {}).items():
                print(f"\n--- {format_name} ---")
                print(content)
                
            # Se houver erro, exibe também
            if "error" in result:
                print(f"\nAVISO: {result['error']}")
        else:
            print("\nNenhum prompt foi gerado. Verifique os logs para mais detalhes.")
            if "error" in result:
                print(f"\nERRO: {result['error']}")
            
    except Exception as e:
        print(f"\nERRO CRÍTICO: {str(e)}")
        logger.critical(f"Erro crítico na execução: {str(e)}")
        logger.critical(traceback.format_exc()) 