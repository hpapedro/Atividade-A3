# 📱 Atividade A3 - Análise de Dados de Conversas do WhatsApp

Aplicação web completa desenvolvida em **Python** utilizando **Streamlit**, **Pandas** e **Plotly Express** para processamento, mineração e visualização analítica de dados de conversas exportadas do WhatsApp (compatível com exportações originadas de **Android** e **iOS**).

---

## 🛠️ Tecnologias Utilizadas

- **[Python 3.10+](https://www.python.org/):** Linguagem base do projeto.
- **[Streamlit](https://streamlit.io/):** Framework para construção de interfaces web interativas.
- **[Pandas](https://pandas.pydata.org/):** Biblioteca para ingestão, manipulação, agregação e limpeza dos dados.
- **[Plotly Express](https://plotly.com/python/plotly-express/):** Biblioteca para renderização de gráficos interativos com tooltips e zoom.
- **RegEx (Expressões Regulares):** Extração robusta de metadados de data, hora, remetente e mensagem.

---

## 🚀 Como Executar o Projeto

### 1. Clonar o Repositório
```bash
git clone https://github.com/hpapedro/Atividade-A3.git
cd Atividade-A3
```

### 2. Instalar as Dependências
Com o Python instalado, execute no terminal:
```bash
pip install -r requirements.txt
```
*(ou instale manualmente com: `pip install pandas streamlit plotly`)*

### 3. Executar a Aplicação Web
Inicie o servidor do Streamlit:
```bash
streamlit run app.py
```
*(Caso o comando direto não seja encontrado no Windows, utilize: `py -m streamlit run app.py`)*

A aplicação será aberta automaticamente em seu navegador padrão no endereço:
👉 **`http://localhost:8501`**

---

## 📂 Estrutura de Arquivos

```text
Atividade-A3/
│
├── .streamlit/
│   └── config.toml          # Configuração global de tema unificado (Bege & Alto Contraste)
├── app.py                   # Código-fonte principal da aplicação web
├── conversa.txt             # Arquivo fonte da conversa exportada sem mídia do WhatsApp
├── requirements.txt         # Lista de dependências do projeto
├── .gitignore               # Arquivos e diretórios desconsiderados pelo Git
└── README.md                # Documentação detalhada do projeto
```

---

## ⚙️ Processamento e Estruturação dos Dados

A função de processamento (`carregar_e_processar_dados`) foi construída para atender com robustez aos diferentes formatos de exportação do WhatsApp:

1. **Compatibilidade Multiplataforma:**
   - **Formato Android:** `22/10/2023, 14:35 - Nome: Mensagem`
   - **Formato iOS:** `[22/10/2023, 14:35:12] Nome: Mensagem`
2. **Tratamento de Mensagens em Múltiplas Linhas:** Linhas de texto adicionais de uma mesma mensagem são automaticamente anexadas ao remetente anterior.
3. **Limpeza de Caracteres Invisíveis:** Remoção automática de caracteres especiais de controle do WhatsApp (como `\u200e` LTR mark, `\ufeff` BOM e `\u202f` narrow non-breaking space).
4. **Remoção de Mensagens do Sistema:** Exclusão de mensagens automáticas de sistema (ex: criptografia de ponta a ponta, entradas e saídas de membros, alterações de foto ou assunto).
5. **Estrutura Final Estrita:** O DataFrame final é composto exatamente pelas 4 colunas requeridas:
   - `data` (Data formatada em DD/MM/AAAA)
   - `hora` (Horário do envio)
   - `nome do remetente` (Nome do contato ou participante)
   - `mensagem` (Conteúdo textual da mensagem)

---

## 🎯 Módulos e Opções de Análise Disponíveis

A interface conta com um resumo inicial de métricas gerais e o **DataFrame completo** com as 4 colunas. Logo abaixo, encontram-se as 5 opções de análise organizadas em abas:

### 📊 Opção 1: Resumo das conversas
- Apresenta uma tabela listando os remetentes e a coluna **`total de conversas`** para cada um.
- Os registros são rigorosamente ordenados do remetente com maior quantidade de envios para o menor.

### 👤 Opção 2: Histórico do remetente
- Permite selecionar qualquer remetente por meio de um menu de seleção (`selectbox`).
- Exibe a tabela filtrada contendo as colunas **data**, **hora** e **mensagem**.
- Inclui um **campo de busca em tempo real**: ao digitar qualquer termo, a tabela exibe instantaneamente apenas as mensagens daquele remetente que contêm exatamente o texto digitado.

### 📈 Opção 3: Gráfico do histórico do remetente (Histograma)
- Histograma diário interativo gerado via **Plotly Express**.
- Exibe o volume de conversas por dia para o remetente selecionado.
  - **Eixo X:** Data
  - **Eixo Y:** Quantidade de conversas

### 🍕 Opção 4: Gráfico de pizza
- Gráfico circular (`px.pie`) demonstrando visualmente a fatia percentual de mensagens de cada remetente em relação ao volume total do grupo.

### 📉 Opção 5: Gráfico de linhas
- Gráfico temporal (`px.line`) apresentando o volume diário de mensagens ao longo do tempo para **todos os participantes simultaneamente**.
- Cada participante possui uma linha com uma cor distinta identificada pela legenda.

---

## 🛡️ Tratamento de Erros

A aplicação implementa blocos `try-except` para garantir estabilidade:
- Caso o arquivo `conversa.txt` não seja localizado no diretório raiz, um alerta amigável (`st.error`) orienta o usuário sobre como exportar a conversa sem mídia e posicioná-la na pasta com o nome correto.
- Tratamento de exceções gerais durante o processamento de datas e codificação de caracteres.

---

## 👨‍💻 Autor

- **Pedro Alves**
- Repositório: [hpapedro/Atividade-A3](https://github.com/hpapedro/Atividade-A3)
