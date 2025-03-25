# 🚀 Gerador de Prompts Inteligente

Um sistema avançado para criar prompts bem estruturados para modelos de IA generativa (como ChatGPT, Claude, Gemini), seguindo as melhores práticas de engenharia de prompt.

![Versão](https://img.shields.io/badge/versão-1.0.0-blue)

## 📋 Visão Geral

O **Gerador de Prompts** é uma aplicação Streamlit que utiliza modelos de linguagem avançados para analisar os requisitos do usuário e gerar prompts otimizados em diversos formatos (Markdown, JSON, XML), facilitando a obtenção de resultados consistentes em sistemas de IA.

## ✨ Recursos

- **Múltiplos formatos** - Markdown, JSON e XML
- **Interface amigável** - Interface Streamlit moderna e responsiva
- **Processamento robusto** - Sistema capaz de lidar com erros graciosamente
- **Modo de alta confiabilidade** - Opção de processamento sequencial para maior estabilidade
- **Histórico de prompts** - Armazena e permite revisitar prompts gerados anteriormente
- **Exemplos prontos** - Modelos pré-configurados para casos de uso comuns

## 🖥️ Capturas de Tela

*(Adicione capturas de tela aqui)*

## 🛠️ Tecnologias

- [Streamlit](https://streamlit.io/) - Framework de interface
- [LangChain](https://python.langchain.com/) - Framework para integração com LLMs
- [LangGraph](https://github.com/langchain-ai/langgraph) - Biblioteca para orquestração de fluxos
- [OpenAI API](https://openai.com/blog/openai-api) - Modelos de linguagem

## 🚦 Pré-requisitos

- Python 3.9+
- Conta na OpenAI com API key

## ⚙️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/prompt-generator.git
cd prompt-generator
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure sua API key da OpenAI:
```bash
# No Windows
echo OPENAI_API_KEY=sua-chave-api > .env

# No Linux/MacOS
echo "OPENAI_API_KEY=sua-chave-api" > .env
```

4. Execute a aplicação:
```bash
streamlit run app.py
```

## 🔍 Uso

1. Na aba "Gerar Prompt", descreva o prompt que você gostaria de criar
2. Especifique o objetivo, formato(s) desejado(s), tom e quaisquer restrições
3. Utilize as opções avançadas para personalizar o processamento
4. Clique em "Gerar Prompt" para iniciar o processo
5. Visualize, copie ou baixe os formatos gerados

### 📝 Exemplo de entrada

```
Crie um prompt para gerar histórias de ficção científica com protagonistas não-humanos, 
no formato Markdown, com tom aventureiro e limite de 500 palavras.
```

## 📂 Estrutura do Projeto

```
prompt-generator/
├── app.py                  # Aplicativo Streamlit principal
├── requirements.txt        # Dependências do projeto
├── .env                    # Configurações de ambiente (não versionado)
├── src/
│   ├── main.py             # Ponto de entrada para o fluxo de processamento
│   ├── logger.py           # Configuração de logging
│   ├── requirements_collector.py  # Coleta requisitos do usuário
│   ├── prompt_planner.py   # Planeja a estrutura do prompt
│   ├── format_generator.py # Gera os formatos solicitados
│   └── validation.py       # Validação dos formatos gerados
└── docs/
    └── examples.md         # Exemplos de prompts e saídas
```

## 🔄 Fluxo de Processamento

1. **Coleta de Requisitos**: Analisa a entrada do usuário para extrair objetivos, formatos e outras especificações
2. **Planejamento do Prompt**: Cria uma estrutura base para o prompt com base nos requisitos
3. **Geração de Formatos**: Transforma o rascunho em formatos específicos (Markdown, JSON, XML)
4. **Validação**: Verifica se os formatos atendem às especificações técnicas

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para:

1. Abrir issues para reportar bugs ou sugerir melhorias
2. Enviar pull requests com novos recursos ou correções
3. Compartilhar feedback sobre a usabilidade

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 👏 Agradecimentos

- OpenAI pela API que alimenta os modelos
- Equipe Streamlit pelo framework de interface
- Comunidade LangChain pelos recursos de integração com LLMs

---

Desenvolvido com ❤️ para a comunidade de IA.
