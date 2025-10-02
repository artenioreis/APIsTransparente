# -*- coding: utf-8 -*-
"""
Projeto de Automação e Análise de Dados - Ceará Transparente
Automação para extração e análise de dados de contratos e convênios
"""

# =============================================================================
# 1. IMPORTANDO BIBLIOTECAS NECESSÁRIAS
# =============================================================================

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import warnings
import time
from sqlalchemy import create_engine
import sqlite3

# Configurações de visualização
plt.style.use('default')
sns.set_palette("husl")
warnings.filterwarnings('ignore')

# =============================================================================
# 2. PARÂMETROS E CONFIGURAÇÕES
# =============================================================================

# URLs das APIs base (sem parâmetros de paginação)
BASE_URL_CONVENIOS = 'https://api-dados-abertos.cearatransparente.ce.gov.br/transparencia/contratos/convenios'
BASE_URL_CONTRATOS = 'https://api-dados-abertos.cearatransparente.ce.gov.br/transparencia/contratos/contratos'

# Parâmetros de data para filtro
params = {
    'data_assinatura_inicio': '01/01/2024',
    'data_assinatura_fim': '31/12/2024'
}

# =============================================================================
# 3. FUNÇÕES PARA COLETA DE DADOS
# =============================================================================

def fazer_requisicao_api(url, params=None):
    """
    Faz requisição para a API e retorna os dados
    
    Parameters:
    url (str): URL da API
    params (dict): Parâmetros da requisição
    
    Returns:
    dict: Dados da resposta da API
    """
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # Levanta exceção para erros HTTP
        
        print(f"✅ Requisição bem-sucedida para: {url}")
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def extrair_todas_paginas(url_base, params, max_paginas=10):
    """
    Extrai dados de todas as páginas disponíveis na API
    
    Parameters:
    url_base (str): URL base da API
    params (dict): Parâmetros da requisição
    max_paginas (int): Número máximo de páginas a extrair
    
    Returns:
    list: Lista com todos os registros
    """
    todos_dados = []
    
    for pagina in range(1, max_paginas + 1):
        print(f"📄 Extraindo página {pagina}...")
        
        # Adiciona parâmetro de página
        params_pagina = params.copy()
        params_pagina['page'] = pagina
        
        dados = fazer_requisicao_api(url_base, params_pagina)
        
        if dados and 'data' in dados and dados['data']:
            todos_dados.extend(dados['data'])
            print(f"   ✅ {len(dados['data'])} registros extraídos")
            
            # Verifica se há mais páginas
            if len(dados['data']) < 15:  # Supondo 15 registros por página
                print("🏁 Última página alcançada")
                break
                
            # Pequena pausa para não sobrecarregar a API
            time.sleep(0.5)
        else:
            print("🚫 Nenhum dado encontrado ou fim dos dados")
            break
    
    print(f"🎯 Total de registros extraídos: {len(todos_dados)}")
    return todos_dados

# =============================================================================
# 4. EXTRAÇÃO DE DADOS - CONVÊNIOS
# =============================================================================

print("=" * 60)
print("🚀 INICIANDO EXTRAÇÃO DE DADOS - CONVÊNIOS")
print("=" * 60)

# Extraindo dados de convênios
dados_convenios = extrair_todas_paginas(BASE_URL_CONVENIOS, params, max_paginas=5)

# Convertendo para DataFrame
if dados_convenios:
    df_convenios = pd.DataFrame(dados_convenios)
    print(f"📊 DataFrame Convênios criado: {df_convenios.shape}")
else:
    df_convenios = pd.DataFrame()
    print("⚠️  Nenhum dado de convênios extraído")

# =============================================================================
# 5. EXTRAÇÃO DE DADOS - CONTRATOS
# =============================================================================

print("\n" + "=" * 60)
print("🚀 INICIANDO EXTRAÇÃO DE DADOS - CONTRATOS")
print("=" * 60)

# Extraindo dados de contratos
dados_contratos = extrair_todas_paginas(BASE_URL_CONTRATOS, params, max_paginas=5)

# Convertendo para DataFrame
if dados_contratos:
    df_contratos = pd.DataFrame(dados_contratos)
    print(f"📊 DataFrame Contratos criado: {df_contratos.shape}")
else:
    df_contratos = pd.DataFrame()
    print("⚠️  Nenhum dado de contratos extraído")

# =============================================================================
# 6. EXPLORAÇÃO INICIAL DOS DADOS
# =============================================================================

print("\n" + "=" * 60)
print("🔍 EXPLORAÇÃO INICIAL DOS DADOS")
print("=" * 60)

# Função para explorar dados
def explorar_dataframe(df, nome):
    """
    Função para explorar um DataFrame
    """
    print(f"\n📋 EXPLORAÇÃO: {nome}")
    print("-" * 40)
    
    if df.empty:
        print("DataFrame vazio")
        return
    
    print(f"📐 Dimensões: {df.shape}")
    print(f"📝 Colunas: {list(df.columns)}")
    print("\n📊 Informações básicas:")
    print(df.info())
    
    print("\n🔢 Estatísticas descritivas:")
    print(df.describe())
    
    print("\n🔍 Primeiras linhas:")
    print(df.head(3))

# Explorando os DataFrames
explorar_dataframe(df_convenios, "CONVÊNIOS")
explorar_dataframe(df_contratos, "CONTRATOS")

# =============================================================================
# 7. PRÉ-PROCESSAMENTO E LIMPEZA DE DADOS
# =============================================================================

print("\n" + "=" * 60)
print("🧹 PRÉ-PROCESSAMENTO E LIMPEZA DE DADOS")
print("=" * 60)

def preprocessar_dados(df, tipo):
    """
    Função para pré-processar os dados
    
    Parameters:
    df (DataFrame): DataFrame a ser processado
    tipo (str): Tipo de dados ('convenios' ou 'contratos')
    
    Returns:
    DataFrame: DataFrame processado
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Convertendo colunas de data
    colunas_data = ['data_assinatura', 'data_processamento', 'data_termino']
    for coluna in colunas_data:
        if coluna in df_clean.columns:
            df_clean[coluna] = pd.to_datetime(df_clean[coluna], errors='coerce')
    
    # Convertendo colunas numéricas
    colunas_valores = ['valor_contrato', 'valor_aditivo', 'valor_empenhado', 
                      'valor_ajuste', 'valor_pago', 'valor_original_concedente',
                      'valor_original_contrapartida']
    
    for coluna in colunas_valores:
        if coluna in df_clean.columns:
            df_clean[coluna] = pd.to_numeric(df_clean[coluna], errors='coerce')
    
    print(f"✅ Dados {tipo} pré-processados")
    return df_clean

# Aplicando pré-processamento
df_convenios_clean = preprocessar_dados(df_convenios, 'convênios')
df_contratos_clean = preprocessar_dados(df_contratos, 'contratos')

# =============================================================================
# 8. ANÁLISE EXPLORATÓRIA DE DADOS (AED)
# =============================================================================

print("\n" + "=" * 60)
print("📊 ANÁLISE EXPLORATÓRIA DE DADOS (AED)")
print("=" * 60)

def criar_visualizacoes(df, tipo):
    """
    Cria visualizações para análise exploratória
    """
    if df.empty:
        print(f"⚠️  Nenhum dado disponível para {tipo}")
        return
    
    # Configuração para múltiplos gráficos
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Análise Exploratória - {tipo.upper()}', fontsize=16, fontweight='bold')
    
    # 1. Distribuição de valores (se existir coluna de valor)
    colunas_valor = [col for col in df.columns if 'valor' in col.lower()]
    if colunas_valor:
        # Pegando a primeira coluna de valor disponível
        coluna_valor = colunas_valor[0]
        valores_validos = df[coluna_valor].dropna()
        
        if not valores_validos.empty:
            axes[0, 0].hist(valores_validos, bins=20, edgecolor='black', alpha=0.7)
            axes[0, 0].set_title(f'Distribuição de {coluna_valor.replace("_", " ").title()}')
            axes[0, 0].set_xlabel('Valor (R$)')
            axes[0, 0].set_ylabel('Frequência')
            axes[0, 0].ticklabel_format(style='plain', axis='x')
    
    # 2. Contagem por órgão (top 10)
    if 'orgao' in df.columns:
        top_orgaos = df['orgao'].value_counts().head(10)
        axes[0, 1].barh(range(len(top_orgaos)), top_orgaos.values)
        axes[0, 1].set_yticks(range(len(top_orgaos)))
        axes[0, 1].set_yticklabels(top_orgaos.index, fontsize=8)
        axes[0, 1].set_title('Top 10 Órgãos com Mais Contratos/Convênios')
        axes[0, 1].set_xlabel('Quantidade')
    
    # 3. Evolução temporal por mês (se existir data)
    if 'data_assinatura' in df.columns:
        df['mes_assinatura'] = df['data_assinatura'].dt.to_period('M')
        contratos_por_mes = df['mes_assinatura'].value_counts().sort_index()
        
        axes[1, 0].plot(range(len(contratos_por_mes)), contratos_por_mes.values, marker='o')
        axes[1, 0].set_title('Evolução de Contratos/Convênios por Mês')
        axes[1, 0].set_xlabel('Mês')
        axes[1, 0].set_ylabel('Quantidade')
        axes[1, 0].set_xticks(range(len(contratos_por_mes)))
        axes[1, 0].set_xticklabels([str(x) for x in contratos_por_mes.index], rotation=45)
    
    # 4. Modalidade de licitação (se existir)
    if 'descricao_modalidade' in df.columns:
        modalidades = df['descricao_modalidade'].value_counts()
        axes[1, 1].pie(modalidades.values, labels=modalidades.index, autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Distribuição por Modalidade de Licitação')
    
    plt.tight_layout()
    plt.show()
    
    # Estatísticas adicionais
    print(f"\n📈 ESTATÍSTICAS PARA {tipo.upper()}:")
    print("-" * 40)
    
    if colunas_valor:
        coluna_principal = colunas_valor[0]
        print(f"💰 Valor total: R$ {df[coluna_principal].sum():,.2f}")
        print(f"📊 Valor médio: R$ {df[coluna_principal].mean():,.2f}")
        print(f"🎯 Valor máximo: R$ {df[coluna_principal].max():,.2f}")
        print(f"📉 Valor mínimo: R$ {df[coluna_principal].min():,.2f}")
    
    print(f"📅 Período analisado: {params['data_assinatura_inicio']} a {params['data_assinatura_fim']}")
    print(f"🔢 Total de registros: {len(df)}")

# Criando visualizações
criar_visualizacoes(df_convenios_clean, 'Convênios')
criar_visualizacoes(df_contratos_clean, 'Contratos')

# =============================================================================
# 9. ANÁLISE COMPARATIVA ENTRE CONTRATOS E CONVÊNIOS
# =============================================================================

print("\n" + "=" * 60)
print("🔄 ANÁLISE COMPARATIVA")
print("=" * 60)

if not df_convenios_clean.empty and not df_contratos_clean.empty:
    # Encontrando coluna comum de valor para comparação
    coluna_valor_conv = next((col for col in df_convenios_clean.columns if 'valor' in col.lower() and col in df_convenios_clean.columns), None)
    coluna_valor_contr = next((col for col in df_contratos_clean.columns if 'valor' in col.lower() and col in df_contratos_clean.columns), None)
    
    if coluna_valor_conv and coluna_valor_contr:
        # Criando gráfico comparativo
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categorias = ['Convênios', 'Contratos']
        valores_totais = [
            df_convenios_clean[coluna_valor_conv].sum(),
            df_contratos_clean[coluna_valor_contr].sum()
        ]
        
        barras = ax.bar(categorias, valores_totais, color=['skyblue', 'lightcoral'])
        ax.set_title('Comparação: Valor Total - Convênios vs Contratos')
        ax.set_ylabel('Valor Total (R$)')
        ax.ticklabel_format(style='plain', axis='y')
        
        # Adicionando valores nas barras
        for barra, valor in zip(barras, valores_totais):
            altura = barra.get_height()
            ax.text(barra.get_x() + barra.get_width()/2., altura,
                   f'R$ {valor:,.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
        
        print("📊 RESUMO COMPARATIVO:")
        print(f"   Convênios: {len(df_convenios_clean)} registros | Valor total: R$ {valores_totais[0]:,.2f}")
        print(f"   Contratos: {len(df_contratos_clean)} registros | Valor total: R$ {valores_totais[1]:,.2f}")

# =============================================================================
# 10. ARMAZENAMENTO EM BANCO DE DADOS
# =============================================================================

print("\n" + "=" * 60)
print("💾 ARMAZENAMENTO EM BANCO DE DADOS")
print("=" * 60)

def salvar_em_banco(df_convenios, df_contratos):
    """
    Salva os dados em um banco SQLite
    """
    try:
        # Criando conexão com SQLite
        conn = sqlite3.connect('ceara_transparente.db')
        
        # Salvando DataFrames
        if not df_convenios.empty:
            df_convenios.to_sql('convenios', conn, if_exists='replace', index=False)
            print("✅ Dados de convênios salvos no banco")
        
        if not df_contratos.empty:
            df_contratos.to_sql('contratos', conn, if_exists='replace', index=False)
            print("✅ Dados de contratos salvos no banco")
        
        conn.close()
        print("💾 Banco de dados 'ceara_transparente.db' criado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")

# Salvando em banco de dados
salvar_em_banco(df_convenios_clean, df_contratos_clean)

# =============================================================================
# 11. SALVANDO EM ARQUIVOS CSV
# =============================================================================

print("\n" + "=" * 60)
print("📁 SALVANDO EM ARQUIVOS CSV")
print("=" * 60)

# Salvando DataFrames em arquivos CSV
if not df_convenios_clean.empty:
    df_convenios_clean.to_csv('convenios_ceara_transparente.csv', index=False, encoding='utf-8')
    print("✅ Arquivo 'convenios_ceara_transparente.csv' salvo")

if not df_contratos_clean.empty:
    df_contratos_clean.to_csv('contratos_ceara_transparente.csv', index=False, encoding='utf-8')
    print("✅ Arquivo 'contratos_ceara_transparente.csv' salvo")

# =============================================================================
# 12. RELATÓRIO FINAL E INSIGHTS
# =============================================================================

print("\n" + "=" * 60)
print("📋 RELATÓRIO FINAL E INSIGHTS")
print("=" * 60)

print("\n🎯 RESUMO EXECUTIVO DO PROJETO:")
print("-" * 40)
print("""
Este projeto realizou a automação da coleta, processamento e análise de 
dados de contratos e convênios do portal Ceará Transparente, seguindo 
as definições do dicionário de dados fornecido.

📈 PRINCIPAIS ETAPAS CONCLUÍDAS:

1. ✅ Automação da coleta via API
2. ✅ Processamento e limpeza dos dados  
3. ✅ Análise exploratória com visualizações
4. ✅ Armazenamento em banco de dados
5. ✅ Geração de relatórios e insights

🔍 PRINCIPAIS VARIÁVEIS ANALISADAS (conforme dicionário):

• Concedente/Financiador: Origem dos recursos
• Órgão/Secretaria: Unidades gestoras
• Modalidade: Forma de licitação
• Valores: Contrato, aditivo, empenhado, pago, etc.
• Datas: Assinatura, processamento, término
• Objeto: Descrição do que está sendo contratado

💡 RECOMENDAÇÕES:

1. Monitorar regularmente os valores atualizados vs originais
2. Analisar a relação entre valores empenhados e pagos
3. Identificar padrões nas modalidades de licitação
4. Acompanhar a distribuição temporal dos contratos
5. Verificar a aderência aos prazos estabelecidos

🔄 PRÓXIMOS PASSOS SUGERIDOS:

• Expandir análise para períodos históricos
• Implementar alertas para outliers e anomalias
• Desenvolver dashboard interativo
• Integrar com outras fontes de dados de transparência
""")

# =============================================================================
# 13. VALIDAÇÃO E QUALIDADE DOS DADOS
# =============================================================================

print("\n" + "=" * 60)
print("🔎 VALIDAÇÃO E QUALIDADE DOS DADOS")
print("=" * 60)

def validar_qualidade_dados(df, nome):
    """
    Realiza validação da qualidade dos dados
    """
    if df.empty:
        print(f"⚠️  Nenhum dado para validar em {nome}")
        return
    
    print(f"\n📋 VALIDAÇÃO - {nome}:")
    print(f"   Total de registros: {len(df)}")
    print(f"   Colunas: {len(df.columns)}")
    
    # Verificando valores nulos
    nulos = df.isnull().sum()
    colunas_com_nulos = nulos[nulos > 0]
    
    if not colunas_com_nulos.empty:
        print("   ⚠️  Colunas com valores nulos:")
        for coluna, qtd_nulos in colunas_com_nulos.items():
            percentual = (qtd_nulos / len(df)) * 100
            print(f"      • {coluna}: {qtd_nulos} ({percentual:.1f}%)")
    else:
        print("   ✅ Nenhum valor nulo encontrado")
    
    # Verificando duplicatas
    duplicatas = df.duplicated().sum()
    if duplicatas > 0:
        print(f"   ⚠️  Registros duplicados: {duplicatas}")
    else:
        print("   ✅ Nenhum registro duplicado")

# Validando qualidade dos dados
validar_qualidade_dados(df_convenios_clean, "CONVÊNIOS")
validar_qualidade_dados(df_contratos_clean, "CONTRATOS")

print("\n" + "=" * 60)
print("🎉 PROJETO CONCLUÍDO COM SUCESSO!")
print("=" * 60)
print("""
Os dados foram coletados, processados, analisados e armazenados conforme
o projeto definido. O processo está pronto para ser expandido e otimizado.

📁 ARQUIVOS GERADOS:
• ceara_transparente.db (banco SQLite)
• convenios_ceara_transparente.csv
• contratos_ceara_transparente.csv

🚀 PRÓXIMOS PASSOS: 
Execute novamente para atualizar os dados ou expanda a análise conforme necessário.
""")