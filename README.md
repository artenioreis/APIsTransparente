📊 Automação e Análise de Dados do Portal Ceará Transparente
Este projeto é um pipeline completo para automação da coleta, tratamento, análise e distribuição de dados públicos de contratos e convênios, utilizando a API de Dados Abertos do portal Ceará Transparente.

O script foi desenvolvido para ser executado de forma automatizada, gerando relatórios, gráficos, arquivos de dados e enviando um resumo por e-mail para os destinatários configurados.

✨ Funcionalidades
Extração de Dados via API: Coleta automática de dados de contratos e convênios, com tratamento de paginação para buscar todos os registros disponíveis.

Limpeza e Pré-processamento: Conversão e padronização de tipos de dados (datas e valores numéricos) para garantir a consistência da análise.

Análise Exploratória (EDA): Geração de um painel de gráficos para entender a distribuição dos valores, os órgãos com mais registros, a evolução temporal e as modalidades mais utilizadas.

Análise Comparativa: Visualizações que comparam o volume total e a quantidade de registros entre contratos e convênios.

Armazenamento Persistente: Salvamento dos dados tratados em um banco de dados SQLite (ceara_transparente.db) e em arquivos CSV.

Relatório por E-mail: Envio automático de um e-mail formatado em HTML com um resumo da análise e todos os arquivos gerados (gráficos, CSVs, banco de dados) em anexo para uma lista de destinatários.

Automação de Execução: Um script de lote (.bat) que instala as dependências e executa o notebook de ponta a ponta usando papermill.

🛠️ Tecnologias Utilizadas
Python 3

Jupyter Notebook

Pandas: Para manipulação e análise de dados.

Requests: Para realizar as chamadas à API.

Matplotlib & Seaborn: Para a geração dos gráficos.

SQLite: Para o armazenamento dos dados em banco.

Papermill: Para a execução parametrizada e automatizada do notebook.

🚀 Como Executar o Projeto
Pré-requisitos
Python 3.x instalado.

Git (opcional, para clonar o repositório).

Passos para Execução
Clone o repositório:

Bash

git clone <URL-do-seu-repositorio>
cd <nome-do-repositorio>
Crie e ative um ambiente virtual (Recomendado):

Bash

python -m venv .venv
.\.venv\Scripts\activate
Configure os Destinatários e Remetente do E-mail:

Abra o arquivo ceara_transparente.ipynb.

Na Célula 29 (seção de envio de e-mail), edite as seguintes variáveis:

EMAIL_REMETENTE: Coloque o seu e-mail do Gmail.

SENHA_REMETENTE: Coloque uma senha de aplicativo gerada para sua conta Google. (Não use sua senha principal).

EMAILS_DESTINATARIOS: Adicione os e-mails que receberão o relatório.

Execute o Script de Automação:

Dê um duplo clique no arquivo executar_ceara.bat.

O script irá instalar as dependências do requirements.txt e executar todo o processo do notebook.

Ao final da execução, os arquivos serão gerados no diretório principal e um notebook com a saída da execução será salvo na pasta logs/.

📁 Estrutura do Projeto e Saídas
ceara_transparente.ipynb: O notebook principal com todo o código do pipeline.

executar_ceara.bat: Script para automatizar a execução em ambiente Windows.

requirements.txt: Lista de dependências Python para o projeto.

ceara_transparente.db: (Saída) Banco de dados SQLite com as tabelas convenios e contratos.

*.csv: (Saída) Arquivos CSV com os dados brutos de convênios and contratos.

*.png: (Saída) Gráficos gerados durante a análise exploratória.

relatorio_analitico.txt: (Saída) Um resumo textual com as principais estatísticas.

logs/ceara_transparente_output.ipynb: (Saída) Cópia do notebook com todas as células executadas e seus resultados.

👤 Autor
Artenio Reis****
