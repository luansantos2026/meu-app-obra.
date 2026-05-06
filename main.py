import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Orçamentista Pro", layout="wide")

# --- INICIALIZAÇÃO DE DADOS ---
if 'servicos' not in st.session_state:
    st.session_state.servicos = pd.DataFrame(columns=["Descrição", "Valor (R$)"])

if 'materiais' not in st.session_state:
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)"])

if 'cliente' not in st.session_state:
    st.session_state.cliente = {"nome": "", "obra": "", "contato": ""}

# --- BARRA LATERAL: DADOS DO CLIENTE ---
st.sidebar.header("👤 Dados do Cliente")
st.session_state.cliente["nome"] = st.sidebar.text_input("Nome do Cliente", st.session_state.cliente["nome"])
st.session_state.cliente["obra"] = st.sidebar.text_input("Endereço da Obra", st.session_state.cliente["obra"])
st.session_state.cliente["contato"] = st.sidebar.text_input("Telefone/Contato", st.session_state.cliente["contato"])

st.title(f"📄 Orçamento: {st.session_state.cliente['nome']}")

# --- NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["⚒️ Mão de Obra (Pedreiro)", "🧱 Materiais (Cliente)", "💾 Gerar Orçamento Final"])

# ABA 1: MÃO DE OBRA
with tab1:
    st.header("Serviços do Pedreiro")
    with st.form("form_servico"):
        col1, col2 = st.columns([3, 1])
        desc_serv = col1.text_input("Descrição do Serviço")
        val_serv = col2.number_input("Valor da Mão de Obra (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar Serviço"):
            if desc_serv:
                novo_serv = pd.DataFrame([{"Descrição": desc_serv, "Valor (R$)": val_serv}])
                st.session_state.servicos = pd.concat([st.session_state.servicos, novo_serv], ignore_index=True)
                st.rerun()

    st.table(st.session_state.servicos)
    total_mao_obra = st.session_state.servicos["Valor (R$)"].sum()
    st.metric("Subtotal Mão de Obra", f"R$ {total_mao_obra:,.2f}")

# ABA 2: MATERIAIS
with tab2:
    st.header("Lista de Materiais para o Cliente")
    with st.form("form_mat"):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
        it = c1.text_input("Nome do Material")
        qt = c2.number_input("Quantidade", min_value=0.0)
        un = c3.selectbox("Unid.", ["Sacos", "m²", "Unid", "Latas", "Metros", "Lts"])
        pr = c4.number_input("Preço Unit. Estimado (R$)", min_value=0.0)
        
        if st.form_submit_button("Adicionar Material"):
            if it:
                total_it = qt * pr
                novo_mat = pd.DataFrame([{"Item": it, "Quantidade": qt, "Unidade": un, "Preço Unit. (R$)": pr, "Total (R$)": total_it}])
                st.session_state.materiais = pd.concat([st.session_state.materiais, novo_mat], ignore_index=True)
                st.rerun()

    st.dataframe(st.session_state.materiais, use_container_width=True)
    total_materiais = st.session_state.materiais["Total (R$)"].sum()
    st.metric("Subtotal Materiais", f"R$ {total_materiais:,.2f}")

# ABA 3: PDF COM CAMPOS DE ASSINATURA
with tab3:
    st.header("Exportar Orçamento e Contrato")
    total_geral = total_mao_obra + total_materiais
    
    col_res1, col_res2 = st.columns(2)
    col_res1.write(f"**Mão de Obra:** R$ {total_mao_obra:,.2f}")
    col_res1.write(f"**Materiais:** R$ {total_materiais:,.2f}")
    col_res2.subheader(f"Total: R$ {total_geral:,.2f}")
    
    if st.button("Gerar PDF com Assinaturas"):
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, "ORÇAMENTO DETALHADO DE OBRA", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", '', 11)
        pdf.cell(190, 7, f"Cliente: {st.session_state.cliente['nome']}", ln=True)
        pdf.cell(190, 7, f"Obra: {st.session_state.cliente['obra']}", ln=True)
        pdf.cell(190, 7, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(10)

        # MÃO DE OBRA
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, " SE
