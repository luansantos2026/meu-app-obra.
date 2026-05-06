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
tab1, tab2, tab3 = st.tabs(["⚒️ Mão de Obra", "🧱 Materiais", "💾 Gerar Orçamento PDF"])

# ABA 1: MÃO DE OBRA (SERVIÇOS DO PEDREIRO)
with tab1:
    st.header("Valores de Mão de Obra")
    with st.form("form_servico"):
        col1, col2 = st.columns([3, 1])
        desc_serv = col1.text_input("Descrição do Serviço (Ex: Reboco de 50m²)")
        val_serv = col2.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar Serviço"):
            if desc_serv:
                novo_serv = pd.DataFrame([{"Descrição": desc_serv, "Valor (R$)": val_serv}])
                st.session_state.servicos = pd.concat([st.session_state.servicos, novo_serv], ignore_index=True)
                st.rerun()

    st.subheader("Resumo dos Serviços")
    st.table(st.session_state.servicos)
    total_mao_obra = st.session_state.servicos["Valor (R$)"].sum()
    st.metric("Total Mão de Obra", f"R$ {total_mao_obra:,.2f}")

# ABA 2: MATERIAIS (LISTA DETALHADA)
with tab2:
    st.header("Lista de Materiais Necessários")
    with st.form("form_mat"):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
        it = c1.text_input("Nome do Material")
        qt = c2.number_input("Quantidade", min_value=0.0)
        un = c3.selectbox("Unid.", ["Sacos", "m²", "Unid", "Latas", "Metros"])
        pr = c4.number_input("Preço Estimado Unit. (R$)", min_value=0.0)
        
        if st.form_submit_button("Adicionar Material"):
            if it:
                total_it = qt * pr
                novo_mat = pd.DataFrame([{"Item": it, "Quantidade": qt, "Unidade": un, "Preço Unit. (R$)": pr, "Total (R$)": total_it}])
                st.session_state.materiais = pd.concat([st.session_state.materiais, novo_mat], ignore_index=True)
                st.rerun()

    st.subheader("Lista para Compra")
    st.dataframe(st.session_state.materiais, use_container_width=True)
    total_materiais = st.session_state.materiais["Total (R$)"].sum()
    st.metric("Estimativa de Materiais", f"R$ {total_materiais:,.2f}")

# ABA 3: PDF PROFISSIONAL
with tab3:
    st.header("Finalizar e Exportar")
    total_geral = total_mao_obra + total_materiais
    st.subheader(f"Valor Total do Orçamento: R$ {total_geral:,.2f}")
    
    if st.button("Gerar Orçamento em PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        # Cabeçalho
        pdf.cell(190, 10, "ORÇAMENTO DE CONSTRUÇÃO", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", '', 12)
        pdf.cell(190, 8, f"Cliente: {st.session_state.cliente['nome']}", ln=True)
        pdf.cell(190, 8, f"Obra: {st.session_state.cliente['obra']}", ln=True)
        pdf.cell(190, 8, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(10)

        # MÃO DE OBRA
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, "1. SERVIÇOS DE MÃO DE OBRA", ln=True)
        pdf.set_font("Arial", '', 10)
        for _, row in st.session_state.servicos.iterrows():
            pdf.cell(150, 8, f"- {row['Descrição']}", border=0)
            pdf.cell(40, 8, f"R$ {row['Valor (R$)']:,.2f}", border=0, ln=True, align='R')
        pdf.ln(5)

        # MATERIAIS
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(190, 10, "2. MATERIAIS (ESTIMATIVA)", ln=True)
        pdf.set_font("Arial", '', 10)
        # Cabeçalho da tabela de materiais
        pdf.cell(80, 8, "Item", border=1)
        pdf.cell(30, 8, "Qtd", border=1)
        pdf.cell(40, 8, "V. Unit", border=1)
        pdf.cell(40, 8, "Total", border=1, ln=True)
        
        for _, row in st.session_state.materiais.iterrows():
            pdf.cell(80, 8, str(row['Item']), border=1)
            pdf.cell(30, 8, f"{row['Quantidade']} {row['Unidade']}", border=1)
            pdf.cell(40, 8, f"R$ {row['Preço Unit. (R$)']:,.2f}", border=1)
            pdf.cell(40, 8, f"R$ {row['Total (R$)']:,.2f}", border=1, ln=True)
        pdf.ln(10)

        # TOTAL GERAL
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, f"VALOR TOTAL DO ORÇAMENTO: R$ {total_geral:,.2f}", ln=True, align='R')
        
        pdf_file = "orcamento_cliente.pdf"
        pdf.output(pdf_file)
        
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Baixar Orçamento PDF", f, file_name=pdf_file)
