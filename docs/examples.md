# Exemplos de Uso do Gerador de Prompts

Este documento contém exemplos de prompts para ajudar você a começar com o sistema de geração de prompts.

## Exemplos de Entrada

### 1. História de Ficção Científica

```
Crie um prompt para gerar histórias de ficção científica com protagonistas não-humanos, 
no formato Markdown, com tom aventureiro e limite de 500 palavras. 
O prompt deve incentivar descrições vívidas de mundos alienígenas.
```

### 2. Extração de Dados de Currículo

```
Gere um prompt em formato JSON para extrair informações de currículos, incluindo 
campos para experiência profissional, educação, habilidades técnicas e idiomas. 
O tom deve ser formal e o prompt deve priorizar a captura de datas e durações 
precisas para cada experiência.
```

### 3. Chatbot de Atendimento

```
Crie um prompt XML para um chatbot de atendimento ao cliente para loja de eletrônicos, 
que inclua regras de engajamento, tom amigável, e fluxo de conversa estruturado. 
O chatbot deve ser capaz de lidar com consultas sobre garantia, devoluções e 
especificações técnicas dos produtos.
```

### 4. Resumo Acadêmico

```
Gere um prompt para criar resumos de artigos científicos mantendo os pontos-chave, 
metodologia e conclusões. Formato Markdown, tom formal e objetivo. O resumo não 
deve exceder 250 palavras e deve preservar as referências numéricas do texto original.
```

### 5. Múltiplos Formatos

```
Crie um prompt para gerar descrições de produtos para um catálogo de móveis, 
nos formatos JSON e Markdown. O prompt deve orientar a inclusão de dimensões, 
materiais, estilos e sugestões de uso. O tom deve ser profissional com toques
de entusiasmo para destacar características únicas.
```

## Exemplos de Saída

### Exemplo de Saída Markdown

```markdown
# Prompt: Geração de História de Ficção Científica

## Objetivo
Crie uma história de ficção científica com protagonistas não-humanos, ambientada em um mundo alienígena único e imersivo.

## Formato
A história deve ser estruturada com:
- Título criativo
- Introdução cativante
- Desenvolvimento com conflito claro
- Resolução satisfatória
- Conclusão que deixe espaço para reflexão

## Tom e Estilo
- Tom aventureiro e exploratório
- Linguagem vívida e descritiva
- Perspectiva não-humana consistente
- Elementos de maravilhamento cósmico

## Requisitos
- Limite máximo de 500 palavras
- Protagonista(s) de espécie não-humana com características físicas e culturais detalhadas
- Descrição sensorial rica do ambiente alienígena (aparência, sons, cheiros, texturas)
- Incluir pelo menos um elemento científico plausível
- Evitar tropos comuns de ficção científica

## Exemplos de Elementos
- Ciclos de vida incomuns
- Sistemas sensoriais diferentes dos humanos
- Formas de comunicação não-verbais
- Ecossistemas com relações simbióticas complexas
- Fenômenos físicos ou astronômicos raros

Lembre-se de manter coerência interna no mundo criado, mesmo quando ele desafia as leis da física como as conhecemos.
```

### Exemplo de Saída JSON

```json
{
  "prompt": {
    "title": "Extrator de Informações de Currículos",
    "objective": "Extrair dados estruturados de currículos em formato de texto",
    "output_format": {
      "type": "json",
      "structure": "structured_data"
    },
    "tone": "formal",
    "instruction": "Analise o currículo fornecido e extraia as informações solicitadas, organizando-as de forma estruturada conforme o esquema fornecido. Mantenha a precisão das datas e durações.",
    "extraction_schema": {
      "personal_info": {
        "name": "string",
        "contact": {
          "email": "string",
          "phone": "string",
          "location": "string"
        },
        "links": ["string"]
      },
      "professional_experience": [
        {
          "company": "string",
          "position": "string",
          "start_date": "YYYY-MM",
          "end_date": "YYYY-MM or 'present'",
          "duration": "string",
          "responsibilities": ["string"],
          "achievements": ["string"]
        }
      ],
      "education": [
        {
          "institution": "string",
          "degree": "string",
          "field": "string",
          "start_date": "YYYY-MM",
          "end_date": "YYYY-MM or 'present'",
          "achievements": ["string"]
        }
      ],
      "skills": {
        "technical": ["string"],
        "soft": ["string"]
      },
      "languages": [
        {
          "language": "string",
          "proficiency": "string"
        }
      ],
      "certifications": [
        {
          "name": "string",
          "issuer": "string",
          "date": "YYYY-MM",
          "expires": "YYYY-MM or 'never'"
        }
      ]
    },
    "requirements": [
      "Preserve exact dates in YYYY-MM format",
      "Calculate accurate duration for each experience",
      "Categorize skills appropriately",
      "Maintain hierarchical relationships between positions if evident"
    ]
  }
}
```

### Exemplo de Saída XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt type="customer_service_chatbot">
  <metadata>
    <title>Chatbot de Atendimento para Loja de Eletrônicos</title>
    <version>1.0</version>
    <domain>Electronics Retail</domain>
  </metadata>
  
  <objective>
    Criar um assistente virtual amigável e informativo que auxilie clientes com
    consultas sobre produtos eletrônicos, garantias, devoluções e especificações técnicas.
  </objective>
  
  <tone>
    <primary>Amigável</primary>
    <secondary>Profissional</secondary>
    <tertiary>Solícito</tertiary>
  </tone>
  
  <personality_traits>
    <trait>Paciente</trait>
    <trait>Conhecedor</trait>
    <trait>Eficiente</trait>
    <trait>Solução-orientada</trait>
  </personality_traits>
  
  <conversation_flow>
    <greeting>
      <message>Cumprimentar o cliente de forma amigável e oferecer assistência</message>
      <examples>
        <example>Olá! Bem-vindo à Loja de Eletrônicos. Como posso ajudar hoje?</example>
        <example>Olá! Sou o assistente virtual da Loja de Eletrônicos. Em que posso auxiliar?</example>
      </examples>
    </greeting>
    
    <understanding>
      <message>Compreender a necessidade do cliente através de perguntas clarificadoras</message>
      <examples>
        <example>Você está procurando informações sobre qual tipo de produto?</example>
        <example>Poderia me dar mais detalhes sobre sua dúvida?</example>
      </examples>
    </understanding>
    
    <resolution>
      <message>Fornecer informações precisas e soluções para as consultas do cliente</message>
      <topics>
        <topic id="warranties">
          <details>Explicar políticas de garantia, duração e processo de acionamento</details>
        </topic>
        <topic id="returns">
          <details>Detalhar política de devolução, prazos e procedimentos</details>
        </topic>
        <topic id="specifications">
          <details>Fornecer especificações técnicas detalhadas dos produtos</details>
        </topic>
      </topics>
    </resolution>
    
    <follow_up>
      <message>Verificar se o cliente tem outras dúvidas e oferecer assistência adicional</message>
      <examples>
        <example>Há algo mais em que eu possa ajudar?</example>
        <example>Suas dúvidas foram esclarecidas ou precisa de mais informações?</example>
      </examples>
    </follow_up>
    
    <closing>
      <message>Agradecer ao cliente e encerrar a conversa de forma positiva</message>
      <examples>
        <example>Obrigado por contatar a Loja de Eletrônicos. Tenha um ótimo dia!</example>
        <example>Estamos à disposição sempre que precisar. Até logo!</example>
      </examples>
    </closing>
  </conversation_flow>
  
  <knowledge_base>
    <categories>
      <category id="products">
        <subcategories>
          <subcategory>Smartphones</subcategory>
          <subcategory>Laptops</subcategory>
          <subcategory>TVs</subcategory>
          <subcategory>Áudio</subcategory>
          <subcategory>Acessórios</subcategory>
        </subcategories>
      </category>
      <category id="policies">
        <subcategories>
          <subcategory>Garantia</subcategory>
          <subcategory>Devolução</subcategory>
          <subcategory>Troca</subcategory>
          <subcategory>Entrega</subcategory>
        </subcategories>
      </category>
    </categories>
  </knowledge_base>
  
  <error_handling>
    <scenario type="out_of_scope">
      <response>Informar limites do atendimento e oferecer contato com humano</response>
      <example>Peço desculpas, mas esta questão requer atendimento especializado. Posso transferir para um atendente humano?</example>
    </scenario>
    <scenario type="misunderstood">
      <response>Pedir esclarecimento de forma educada</response>
      <example>Não tenho certeza se compreendi corretamente. Poderia reformular sua pergunta?</example>
    </scenario>
  </error_handling>
</prompt>
```

## Dicas para Melhores Resultados

1. **Seja específico sobre o objetivo** – Quanto mais claro for o propósito do prompt, melhor será o resultado.

2. **Mencione explicitamente os formatos desejados** – Especifique se deseja Markdown, JSON, XML ou múltiplos formatos.

3. **Descreva o tom desejado** – Formal, amigável, técnico, entusiástico, etc.

4. **Inclua restrições ou requisitos especiais** – Como limites de palavras, elementos obrigatórios ou proibidos.

5. **Forneça contexto** – Informações sobre o domínio ou especialidade ajudam a criar prompts mais relevantes. 