#!/usr/bin/env python3
"""
RM4Health Dashboard Local - Versão Simples
Aplicação local que funciona com dados do REDCap
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from redcap_client import REDCapClient
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="RM4Health Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """Carrega dados do REDCap ou arquivo local"""
    try:
        client = REDCapClient()
        if client.test_connection():
            data = client.get_records(raw_or_label='label')
            if data:
                # Salvar backup local
                df = pd.DataFrame(data)
                df.to_csv('backup_redcap_data.csv', index=False)
                return df, "Dados carregados do REDCap via API"
        
        # Se não conseguir conectar, tenta carregar backup
        if os.path.exists('backup_redcap_data.csv'):
            df = pd.read_csv('backup_redcap_data.csv')
            return df, "Dados carregados do backup local (sem VPN)"
        
        return None, "Nenhum dado disponível - conecte à VPN"
        
    except Exception as e:
        return None, f"Erro: {str(e)}"

# Função para gráfico de idade
def create_age_chart(df):
    """Cria gráfico de distribuição por idade"""
    age_fields = ['idade', 'age', 'idade_anos']
    ages = []
    
    for field in age_fields:
        if field in df.columns:
            ages = df[field].dropna()
            ages = pd.to_numeric(ages, errors='coerce').dropna()
            ages = ages[(ages > 0) & (ages < 120)]
            break
    
    if len(ages) > 0:
        fig = px.histogram(
            x=ages, 
            nbins=20, 
            title=f"Distribuição por Idade (n={len(ages)})",
            labels={'x': 'Idade', 'y': 'Frequência'}
        )
        fig.update_layout(showlegend=False)
        return fig
    else:
        return px.bar(x=['Sem dados'], y=[1], title="Dados de idade não encontrados")

# Função para gráfico de gênero
def create_gender_chart(df):
    """Cria gráfico de distribuição por gênero"""
    gender_fields = ['genero', 'gender', 'sexo']
    
    for field in gender_fields:
        if field in df.columns:
            gender_data = df[field].dropna().value_counts()
            if len(gender_data) > 0:
                fig = px.pie(
                    values=gender_data.values, 
                    names=gender_data.index,
                    title=f"Distribuição por Gênero (n={gender_data.sum()})"
                )
                return fig
    
    return px.pie(values=[1], names=['Sem dados'], title="Dados de gênero não encontrados")

# Interface principal
def main():
    # Cabeçalho
    st.title("🏥 RM4Health Dashboard")
    st.markdown("### Sistema de Monitoramento Remoto de Saúde")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Controles")
        
        # Botão para recarregar dados
        if st.button("🔄 Recarregar Dados"):
            st.cache_data.clear()
            st.rerun()
        
        # Status da conexão
        st.header("📡 Status")
        
    # Carregar dados
    df, status_message = load_data()
    
    # Mostrar status
    if df is not None:
        st.success(f"✅ {status_message}")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Registros", len(df))
        
        with col2:
            st.metric("Colunas", len(df.columns))
        
        with col3:
            st.metric("Última Atualização", datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        with col4:
            completude = ((df.notna().sum().sum() / (len(df) * len(df.columns))) * 100)
            st.metric("Completude", f"{completude:.1f}%")
        
        # Tabs para diferentes análises
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "👥 Demografia", "🔍 Dados Raw", "📈 Estatísticas"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(create_age_chart(df), use_container_width=True)
            
            with col2:
                st.plotly_chart(create_gender_chart(df), use_container_width=True)
        
        with tab2:
            st.header("📋 Análise Demográfica")
            
            # Mostrar estatísticas das primeiras colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.subheader("Estatísticas Numéricas")
                st.dataframe(df[numeric_cols].describe())
            
            # Mostrar distribuições categóricas
            categorical_cols = df.select_dtypes(include=['object']).columns[:5]  # Primeiras 5 colunas categóricas
            if len(categorical_cols) > 0:
                st.subheader("Distribuições Categóricas")
                for col in categorical_cols:
                    if df[col].nunique() < 20:  # Só mostrar se tiver menos de 20 valores únicos
                        fig = px.bar(
                            x=df[col].value_counts().index, 
                            y=df[col].value_counts().values,
                            title=f"Distribuição - {col}"
                        )
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.header("🔍 Dados Brutos")
            st.dataframe(df)
            
            # Botão para download
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Baixar dados em CSV",
                data=csv,
                file_name=f"rm4health_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with tab4:
            st.header("📈 Estatísticas Detalhadas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Informações Gerais")
                info_data = {
                    "Total de registros": len(df),
                    "Total de colunas": len(df.columns),
                    "Memória utilizada": f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
                    "Valores nulos": df.isnull().sum().sum(),
                    "Valores únicos": df.nunique().sum()
                }
                
                for key, value in info_data.items():
                    st.metric(key, value)
            
            with col2:
                st.subheader("Colunas com Mais Dados")
                completeness = ((df.notna().sum() / len(df)) * 100).sort_values(ascending=False)
                fig = px.bar(
                    x=completeness.head(10).values,
                    y=completeness.head(10).index,
                    orientation='h',
                    title="Top 10 Colunas por Completude (%)"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error(f"❌ {status_message}")
        st.info("💡 Para usar este dashboard:")
        st.write("1. Conecte-se à VPN da FMUP")
        st.write("2. Verifique as credenciais no arquivo config.py")
        st.write("3. Clique em 'Recarregar Dados'")

if __name__ == "__main__":
    main()
