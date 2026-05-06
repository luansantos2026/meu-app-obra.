import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Gestor de Obra Pro", layout="wide")

# --- INICIALIZAÇÃO DE DADOS ---
if 'gastos' not in st.session_state:
    st.session_state.gastos = pd.DataFrame(columns=["Descrição", "Categoria", "Valor", "Data"])

if 'extras' not in st.session_state:
    st.session_state.extras = pd.DataFrame(columns=["Descrição", "Valor", "Data", "Status"])

if 'materiais' not in st.session_state:
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)", "Status"])

# --- DICIONÁRIO PARA DADOS DO CLIENTE ---
if 'cliente' not in st.session_state:
    st.session_state.cliente = {"nome": "", "obra": "", "data": "", "orcamento": 50000.0}

# Barra Lateral
st.sidebar.header("📋 Dados do Cliente")
st.session_state.cliente["nome"] = st.sidebar.text_input("Nome do Cliente", value=st.session_state.cliente["nome"])
st.session_state.cliente["obra"] = st.sidebar.text_input("Endereço/Obra", value=st.session_state.cliente["obra"])
st.session_state.cliente["orcamento"] = st.sidebar.number_input("Orçamento Contratado (R$)", min_value=0.0, value=st.session_state.cliente["orcamento"])

st.title(f"🏗️ Gestor de Obra: {st.session_state.cliente['nome']}")
st.write(f"**Local:** {st.session_state.cliente['obra']}")

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Financeiro", "➕ Serviços Extras", "📋 Lista de Materiais", "📑 Gerar Relatório PDF"])

# ABA 1: FINANCEIRO
with tab1:
    st.header("Controle de Custos")
    total_gasto = st.session_state.gastos["Valor"].sum()
    saldo = st.session_state.cliente["orcamento"] - total_gasto
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Orçamento Base", f"R$ {st.session_state.cliente['orcamento']:,.2f}")
    col_b.metric("Total Gasto", f"R$ {total_gasto:,.2f}")
    col_c.metric("Saldo Atual", f"R$ {saldo:,.2f}", delta=f"{saldo:,.2f}")
    
    st.subheader("Registros de Gastos")
    st.dataframe(st.session_state.gastos, use_container_width=True)

# ABA 2: EXTRAS
with tab2:
    st.header("Serviços Aditivos (Extras)")
    with st.form("form_extra"):
        d_ex = st.text_input("O que foi pedido extra?")
        v_ex = st.number_input("Valor Extra (R$)", min_value=0.0)
        if st.form_submit_button("Registrar Extra"):
            novo_ex = pd.DataFrame([{"Descrição": d_ex, "Valor": v_ex, "Data": datetime.now().strftime("%d/%m/%Y"), "Status": "Pendente"}])
            st.session_state.extras = pd.concat([st.session_state.extras, novo_ex], ignore_index=True)
            st.rerun()
    st.table(st.session_state.extras)

# ABA 3: LISTA DE MATERIAIS
with tab3:
    st.header("Lista Detalhada de Materiais")
    with st.expander("➕ Adicionar Material"):
        with st.form("form_mat"):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
            it = c1.text_input("Material")
            qt = c2.number_input("Qtd", min_value=0.0)
            un = c3.selectbox("Un", ["m²", "Sacos", "Un", "Kg"])
            pr = c4.number_input("Preço Unitário (R$)", min_value=0.0)
            if st.form_submit_button("Salvar na Lista"):
                total_it = qt * pr
                novo_mat = pd.DataFrame([{"Item": it, "Quantidade": qt, "Unidade": un, "Preço Unit. (R$)": pr, "Total (R$)": total_it, "Status": "Para Comprar"}])
                st.session_state.materiais = pd.concat([st.session_state.materiais, novo_mat], ignore_index=True)
                st.rerun()
    st.dataframe(st.session_state.materiais, use_container_width=True)

# ABA 4: GERADOR DE PDF
with tab4:
    st.header("Gerar Relatório Profissional")
    st.write("Clique no botão abaixo para gerar o PDF com todos os dados preenchidos.")
    
    if st.button("Criar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        # Cabeçalho
        pdf.cell(200, 10, f"RELATORIO DE OBRA - {st.session_state.cliente['nome'].upper()}", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"Obra: {st.session_state.cliente['obra']}", ln=True, align='C')
        pdf.cell(200, 10, f"Data do Relatorio: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='C')
        pdf.ln(10)
        
        # Resumo Financeiro no PDF
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, "RESUMO FINANCEIRO:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, f"Orcamento Base: R$ {st.session_state.cliente['orcamento']:,.2f}", ln=True)
        pdf.cell(200, 10, f"Total Gasto: R$ {st.session_state.gastos['Valor'].sum():,.2f}", ln=True)
        pdf.cell(200, 10, f"Total em Materiais: R$ {st.session_state.materiais['Total (R$)'].sum():,.2f}", ln=True)
        
        # Gerar o arquivo
        nome_pdf = "relatorio_obra.pdf"
        pdf.output(nome_pdf)
        
        with open(nome_pdf, "rb") as f:
            st.download_button("📥 Baixar Relatório PDF", f, file_name=nome_pdf)
