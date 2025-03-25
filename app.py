import streamlit as st
from dotenv import load_dotenv
import os
import json
import traceback
import time
import random
from datetime import datetime

from src.main import run_prompt_generator
from src.logger import logger

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Gerador de Prompts",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para gerar ID único de sessão
def get_session_id():
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
    return st.session_state.session_id

# Função para exibir animação de texto digitado
def typewriter_animation(text, speed=0.03):
    container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text + "▌")
        time.sleep(speed)
    container.markdown(full_text)
    return container

# Função para mostrar o prompt formatado
def display_formatted_prompt(format_name, content, use_expander=True, key_suffix=""):
    # Define a linguagem para o bloco de código
    if format_name.upper() == "JSON":
        language = "json"
    elif format_name.upper() == "XML":
        language = "xml"
    else:
        language = "markdown"
    
    # Cria chaves únicas para os elementos
    download_key = f"dl_{format_name}_{key_suffix}_{get_session_id()}"
    copy_key = f"cp_{format_name}_{key_suffix}_{get_session_id()}"
    
    if use_expander:
        with st.expander(f"📝 Formato: {format_name}", expanded=True):
            # Exibe o conteúdo formatado
            st.code(content, language=language)
            
            # Botões para ações
            col1, col2 = st.columns([1, 5])
            with col1:
                st.download_button(
                    label="⬇️ Baixar",
                    data=content,
                    file_name=f"prompt_{format_name.lower()}_{get_session_id()}.txt",
                    mime="text/plain",
                    help=f"Baixar o prompt no formato {format_name}",
                    key=download_key
                )
            with col2:
                st.button(
                    f"📋 Copiar {format_name}",
                    help=f"Copiar o prompt no formato {format_name} para a área de transferência",
                    on_click=lambda: st.session_state.update({"clipboard": content}),
                    key=copy_key
                )
    else:
        # Versão sem expander para uso em contextos aninhados
        st.markdown(f"**📝 Formato: {format_name}**")
        st.code(content, language=language)
        
        # Botões para ações
        col1, col2 = st.columns([1, 5])
        with col1:
            st.download_button(
                label="⬇️ Baixar",
                data=content,
                file_name=f"prompt_{format_name.lower()}_{get_session_id()}.txt",
                mime="text/plain",
                help=f"Baixar o prompt no formato {format_name}",
                key=download_key
            )
        with col2:
            st.button(
                f"📋 Copiar {format_name}",
                help=f"Copiar o prompt no formato {format_name} para a área de transferência",
                on_click=lambda: st.session_state.update({"clipboard": content}),
                key=copy_key
            )

def main():
    # Custom CSS para melhorar aparência
    st.markdown("""
    <style>
    .big-font {
        font-size:2.5rem !important;
        font-weight:600;
        color:#4CAF50;
    }
    .prompt-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cabeçalho
    st.markdown('<p class="big-font">✨ Gerador de Prompts</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="prompt-header">
    Sistema inteligente para criar prompts bem estruturados para IA generativa,
    seguindo as melhores práticas de engenharia de prompt.
    </div>
    """, unsafe_allow_html=True)
    
    # Verifica se a API key está configurada
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("API Key não configurada no ambiente")
        st.error("⚠️ API Key não configurada. Por favor, crie um arquivo .env com sua OPENAI_API_KEY.")
        st.stop()
    else:
        logger.info(f"API Key configurada: {api_key[:5]}...{api_key[-4:]}")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["🔮 Gerar Prompt", "🔍 Visualizar Histórico", "ℹ️ Ajuda"])
    
    with tab1:
        # Entrada do usuário
        with st.form("prompt_form"):
            user_input = st.text_area(
                "Descreva o prompt que você deseja gerar:",
                height=150,
                placeholder="Ex: Crie um prompt para gerar histórias de ficção científica com protagonistas não-humanos, no formato Markdown, com tom aventureiro..."
            )
            
            # Opções avançadas
            with st.expander("⚙️ Opções avançadas", expanded=False):
                cols = st.columns(3)
                with cols[0]:
                    formato_padrao = st.selectbox(
                        "Formato padrão:",
                        options=["Detectar automaticamente", "Markdown", "JSON", "XML"],
                        index=0,
                        help="Formato padrão caso não seja especificado na descrição"
                    )
                with cols[1]:
                    mostrar_logs = st.checkbox(
                        "Mostrar logs detalhados", 
                        value=False,
                        help="Exibe informações detalhadas de processamento"
                    )
                with cols[2]:
                    usar_pipeline = st.checkbox(
                        "Modo de alta confiabilidade", 
                        value=True,
                        help="Utiliza um pipeline sequencial mais confiável em vez do grafo de processamento"
                    )
            
            # Botão de submissão com estilo personalizado
            submit_col1, submit_col2 = st.columns([3, 1])
            with submit_col2:
                submit_button = st.form_submit_button(
                    "🚀 Gerar Prompt",
                    help="Clique para gerar o prompt com base na sua descrição"
                )
            
            # Armazena as opções na sessão
            if submit_button:
                st.session_state.formato_padrao = formato_padrao
                st.session_state.mostrar_logs = mostrar_logs
                st.session_state.usar_pipeline = usar_pipeline
    
        # Processamento quando o formulário é enviado
        if submit_button and user_input:
            # Registra início do processamento
            start_time = time.time()
            logger.info(f"Formulário enviado com texto de {len(user_input)} caracteres")
            
            # Adiciona formato para detecção se necessário
            if st.session_state.formato_padrao != "Detectar automaticamente" and st.session_state.formato_padrao.lower() not in user_input.lower():
                enhanced_input = f"{user_input}\n\nformato {st.session_state.formato_padrao.lower()}"
                logger.info(f"Adicionando formato padrão: {st.session_state.formato_padrao}")
            else:
                enhanced_input = user_input
            
            # Seção para mostrar o progresso
            st.markdown("### 🔄 Gerando seu prompt...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_output = st.empty()
            
            # Logs em tempo real
            if st.session_state.mostrar_logs:
                log_container = log_output.container()
                log_container.markdown("```\n# Logs de processamento:\n```")
            
            try:
                # Simulação de etapas de processamento visível ao usuário
                steps = [
                    ("Analisando requisitos...", 10),
                    ("Extraindo formato e objetivo...", 30),
                    ("Planejando estrutura do prompt...", 50),
                    ("Aplicando práticas de engenharia de prompt...", 70),
                    ("Gerando formatos solicitados...", 85),
                    ("Finalizando...", 95)
                ]
                
                # Atualiza o progresso visualmente
                for step_msg, percent in steps:
                    status_text.text(step_msg)
                    progress_bar.progress(percent)
                    
                    if st.session_state.mostrar_logs:
                        log_container.markdown(f"```\n# Logs de processamento:\n{step_msg}\n```")
                    
                    # Cria um tempo de espera para cada etapa
                    time.sleep(0.3)
                
                # Executa o gerador de prompt
                result = run_prompt_generator(enhanced_input)
                
                # Finaliza o progresso
                status_text.text("Processamento concluído!")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Limpa exibição do progresso
                progress_bar.empty()
                status_text.empty()
                
                # Verifica se houve erro ou aviso
                if "error" in result:
                    st.warning(f"⚠️ {result['error']}")
                
                # Verifica se há saída
                if "output" in result and result["output"]:
                    # Calculando tempo de processamento
                    processing_time = time.time() - start_time
                    st.success(f"✅ Prompt gerado com sucesso em {processing_time:.2f} segundos!")
                    
                    # Armazena o resultado na sessão
                    st.session_state.result = result
                    st.session_state.last_result_time = datetime.now().strftime("%H:%M:%S")
                    
                    # Salva no histórico
                    if "history" not in st.session_state:
                        st.session_state.history = []
                    
                    st.session_state.history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "input": user_input,
                        "output": result.get("output", {}),
                        "id": get_session_id()
                    })
                    
                    # Limita o histórico a 10 itens
                    if len(st.session_state.history) > 10:
                        st.session_state.history = st.session_state.history[-10:]
                    
                else:
                    st.error("❌ Não foi possível gerar o prompt. Tente novamente com uma descrição diferente.")
                    if st.session_state.mostrar_logs:
                        log_container.markdown(f"```\nErro: {result.get('error', 'Falha desconhecida')}\n```")
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Exceção durante geração do prompt: {error_msg}")
                logger.error(traceback.format_exc())
                st.error(f"❌ Erro ao gerar o prompt: {error_msg}")
                
                # Exibe informações técnicas para debugging
                if st.session_state.mostrar_logs:
                    with st.expander("🔍 Detalhes técnicos do erro", expanded=False):
                        st.code(traceback.format_exc())
        
        # Exibição dos resultados
        if "result" in st.session_state and st.session_state.result.get("output"):
            st.markdown(f"### ✨ Seu Prompt está pronto! ({st.session_state.last_result_time})")
            
            output_data = st.session_state.result["output"]
            
            # Exibe os formatos gerados
            for format_name, content in output_data.items():
                display_formatted_prompt(format_name, content, use_expander=True, key_suffix="main")
    
    # Tab de histórico
    with tab2:
        if "history" in st.session_state and st.session_state.history:
            st.markdown("### 📚 Histórico de Prompts Gerados")
            
            for i, item in enumerate(reversed(st.session_state.history)):
                with st.expander(f"#{i+1} - {item['timestamp']} - {item['input'][:50]}...", expanded=i==0):
                    st.markdown(f"**Entrada original:**")
                    st.text(item['input'])
                    
                    st.markdown(f"**Prompts gerados:**")
                    for format_name, content in item['output'].items():
                        # Usar a versão sem expander para evitar expanders aninhados
                        # Criar chave única baseada no id do item e índice
                        unique_key = f"hist_{i}_{item['id']}"
                        display_formatted_prompt(format_name, content, use_expander=False, key_suffix=unique_key)
        else:
            st.info("📝 Seu histórico de prompts aparecerá aqui depois que você gerar alguns prompts.")
    
    # Tab de ajuda
    with tab3:
        st.markdown("### 📖 Como usar o Gerador de Prompts")
        
        st.markdown("""
        #### 1️⃣ Descreva o prompt desejado
        Na aba "Gerar Prompt", descreva o prompt que você deseja criar, incluindo:
        - **Objetivo principal** do prompt
        - **Formato(s) desejado(s)**: Markdown, JSON, XML
        - **Tom de comunicação** (opcional)
        - **Restrições específicas** (opcional)
        - **Exemplos** (opcional)
        
        #### 2️⃣ Opções avançadas
        - **Formato padrão**: Escolha um formato caso não especifique na descrição
        - **Mostrar logs**: Veja detalhes do processamento
        - **Modo alta confiabilidade**: Usa um processamento mais robusto
        
        #### 3️⃣ Exemplos de entrada
        ```
        Crie um prompt para gerar histórias de ficção científica com protagonistas não-humanos, 
        no formato Markdown, com tom aventureiro.
        ```
        
        ```
        Gere um prompt em formato JSON para criar uma receita de bolo, incluindo 
        campos para ingredientes, tempo de preparo e dificuldade.
        ```
        
        #### 4️⃣ Dicas
        - Seja específico sobre o objetivo final do prompt
        - Mencione explicitamente o formato desejado (Markdown/JSON/XML)
        - Para prompts mais robustos, mencione o tipo de saída esperada
        """)
        
        # Exemplos prontos
        st.markdown("### 🔥 Exemplos Prontos")
        
        exemplo_buttons = [
            "Prompt para gerar história em Markdown",
            "Prompt para extração de dados em JSON",
            "Prompt para chatbot em XML",
            "Prompt para resumo de artigos científicos"
        ]
        
        for exemplo in exemplo_buttons:
            if st.button(exemplo):
                if exemplo == "Prompt para gerar história em Markdown":
                    st.session_state.exemplo_selecionado = (
                        "Crie um prompt para gerar histórias de ficção científica com protagonistas "
                        "não-humanos, no formato Markdown, com tom aventureiro e limite de 500 palavras."
                    )
                elif exemplo == "Prompt para extração de dados em JSON":
                    st.session_state.exemplo_selecionado = (
                        "Gere um prompt em formato JSON para extrair informações de currículos, "
                        "incluindo campos para experiência, educação, habilidades técnicas e idiomas."
                    )
                elif exemplo == "Prompt para chatbot em XML":
                    st.session_state.exemplo_selecionado = (
                        "Crie um prompt XML para um chatbot de atendimento ao cliente para loja de eletrônicos, "
                        "que inclua regras de engajamento, tom amigável, e fluxo de conversa estruturado."
                    )
                elif exemplo == "Prompt para resumo de artigos científicos":
                    st.session_state.exemplo_selecionado = (
                        "Gere um prompt para criar resumos de artigos científicos mantendo os pontos-chave, "
                        "metodologia e conclusões. Formato Markdown, tom formal e objetivo."
                    )
                
                st.info(f"**Exemplo selecionado!** Volte para a aba 'Gerar Prompt' e clique em 'Aplicar Exemplo'.")
        
        if "exemplo_selecionado" in st.session_state:
            st.code(st.session_state.exemplo_selecionado)
    
    # Informações adicionais na barra lateral
    with st.sidebar:
        st.header("Sobre")
        st.info("""
        Este gerador de prompts utiliza:
        - **LangChain** para templates e interação com LLMs
        - **LangGraph** para orquestração de fluxos
        - **Validação de sintaxe** para formatos estruturados
        
        O sistema coleta requisitos, planeja e gera o prompt nos formatos solicitados.
        """)
        
        # Status do sistema
        st.subheader("Status do Sistema")
        
        col1, col2 = st.columns(2)
        with col1:
            if api_key:
                st.success("API OpenAI: ✓")
            else:
                st.error("API OpenAI: ✗")
        with col2:
            st.success("Sistema: Online")
            
        # Exemplo selecionado
        if "exemplo_selecionado" in st.session_state:
            st.subheader("Exemplo Selecionado")
            st.info(st.session_state.exemplo_selecionado[:100] + "...")
            if st.button("Aplicar Exemplo"):
                st.session_state.applied_example = st.session_state.exemplo_selecionado
                st.rerun()
        
        # Créditos
        st.markdown("---")
        st.caption("Desenvolvido com ❤️ usando Streamlit e LangChain")
        st.caption(f"Sessão: {get_session_id()}")

if __name__ == "__main__":
    try:
        logger.info("Iniciando aplicação Streamlit")
        
        # Aplica exemplo se houver
        if "applied_example" in st.session_state:
            example = st.session_state.applied_example
            del st.session_state.applied_example
            # Configura o formulário com o exemplo para ser preenchido
            main()
        else:
            main()
            
    except Exception as e:
        logger.critical(f"Erro fatal na aplicação: {str(e)}")
        logger.critical(traceback.format_exc())
        st.error("Ocorreu um erro crítico na aplicação. Por favor, verifique os logs para mais detalhes.") 