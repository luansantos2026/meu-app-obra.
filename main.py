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

# --- BARRA LATERAL ---
st.sidebar.header("👤 Dados do Cliente")
st.session_state.cliente["nome"] = st.sidebar.text_input("Nome do Cliente", st.session_state.cliente["nome"])
st.sidebar.info("Para limpar o nome, basta apagar o texto acima.")

# Botão de Reset Geral na lateral
st.sidebar.markdown("---")
if st.sidebar.button("🧹 LIMPAR TUDO (Reset Geral)"):
    st.session_state.servicos = pd.DataFrame(columns=["Descrição", "Valor (R$)"])
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)"])
    st.session_state.cliente = {"nome": "", "obra": "", "contato": ""}
    st.rerun()

st.title(f"📄 Orçamento: {st.session_state.cliente['nome']}")

tab1, tab2, tab3 = st.tabs(["⚒️ Mão de Obra", "🧱 Materiais", "💾 Gerar Orçamento"])

# --- ABA 1: MÃO DE OBRA ---
with tab1:
    st.header("Serviços do Pedreiro")
    with st.form("form_servico", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        desc_serv = col1.text_input("Descrição do Serviço")
        val_serv = col2.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            if desc_serv:
                novo = pd.DataFrame([{"Descrição": desc_serv, "Valor (R$)": val_serv}])
                st.session_state.servicos = pd.concat([st.session_state.servicos, novo], ignore_index=True)
                st.rerun()
    
    st.table(st.session_state.servicos)
    
    if not st.session_state.servicos.empty:
        if st.button("🗑️ Limpar Mão de Obra"):
            st.session_state.servicos = pd.DataFrame(columns=["Descrição", "Valor (R$)"])
            st.rerun()

# --- ABA 2: MATERIAIS ---
with tab2:
    st.header("Lista de Materiais")
    with st.form("form_mat", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 2])
        it = c1.text_input("Item")
        qt = c2.number_input("Qtd", min_value=0.0)
        un = c3.selectbox("Un", ["Sacos", "m²", "Un", "Latas", "Metros"])
        pr = c4.number_input("Preço Unit. (R$)", min_value=0.0)
        if st.form_submit_button("Incluir Material"):
            if it:
                total_it = qt * pr
                novo_m = pd.DataFrame([{"Item": it, "Quantidade": qt, "Unidade": un, "Preço Unit. (R$)": pr, "Total (R$)": total_it}])
                st.session_state.materiais = pd.concat([st.session_state.materiais, novo_m], ignore_index=True)
                st.rerun()

    st.dataframe(st.session_state.materiais, use_container_width=True)
    
    if not st.session_state.materiais.empty:
        if st.button("🗑️ Limpar Lista de Materiais"):
            st.session_state.materiais = pd.DataFrame(columns=["Item", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)"])
            st.rerun()

# --- ABA 3: PDF ---
with tab3:
    st.header("Finalizar Orçamento")
    total_mao = st.session_state.servicos["Valor (R$)"].sum()
    total_mat = st.session_state.materiais["Total (R$)"].sum()
    total_geral = total_mao + total_mat
    
    st.subheader(f"Total Geral: R$ {total_geral:,.2f}")
    
    if st.button("Gerar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(190, 10, "ORCAMENTO DE OBRA", ln=True, align='C')
        
        pdf.set_font("Helvetica", '', 10)
        pdf.ln(5)
        pdf.cell(190, 7, f"Cliente: {st.session_state.cliente['nome']}", ln=True)
        pdf.cell(190, 7, f"Obra: {st.session_state.cliente['obra']}", ln=True)
        pdf.ln(10)

        # Mão de Obra no PDF
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, "1. MAO DE OBRA (PEDREIRO)", ln=True)
        pdf.set_font("Helvetica", '', 10)
        for _, r in st.session_state.servicos.iterrows():
            pdf.cell(150, 8, f"- {r['Descrição']}")
            pdf.cell(40, 8, f"R$ {r['Valor (R$)']:,.2f}", ln=True, align='R')
        
        pdf.ln(5)
        # Materiais no PDF
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, "2. MATERIAIS (CLIENTE)", ln=True)
        pdf.set_font("Helvetica", '', 9)
        for _, r in st.session_state.materiais.iterrows():
            pdf.cell(190, 7, f"- {r['Item']}: {r['Quantidade']} {r['Unidade']} (R$ {r['Total (R$)']:,.2f})", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, f"VALOR TOTAL: R$ {total_geral:,.2f}", ln=True, align='R')
        
        # Assinaturas no PDF
        pdf.ln(25)
        y = pdf.get_y()
        pdf.line(20, y, 80, y)
        pdf.line(110, y, 170, y)
        pdf.ln(2)
        pdf.cell(85, 5, "Assinatura Pedreiro", align='C')
        pdf.cell(105, 5, "Assinatura Cliente", align='C')
        
        pdf.output("orcamento.pdf")
        with open("orcamento.pdf", "rb") as f:
            st.download_button("📥 Baixar PDF", f, "orcamento.pdf")
