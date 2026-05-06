import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Orçamentista Pro", layout="wide")

# --- FUNÇÃO DE CORREÇÃO DE ESCRITA ---
def corrigir_texto(texto):
    if not texto: return ""
    texto = texto.strip().capitalize()
    correcoes = {
        "Cimento": ["cimento", "cimeto", "simento"],
        "Treliça": ["trelica", "treliça", "terliça"],
        "Argamassa": ["argamassa", "argamassa", "algamassa"],
        "Elétrica": ["eletrica", "eletrica"],
        "Hidráulica": ["hidraulica", "idraulica"],
        "Vergalhão": ["vergalhao", "vergalhao"]
    }
    for correto, errados in correcoes.items():
        for errado in errados:
            if texto.lower() == errado: return correto
    return texto

# --- INICIALIZAÇÃO DE DADOS ---
if 'servicos' not in st.session_state:
    st.session_state.servicos = pd.DataFrame(columns=["Descrição", "Valor (R$)", "Status"])
if 'materiais' not in st.session_state:
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Medidas", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)"])
if 'cliente' not in st.session_state:
    st.session_state.cliente = {"nome": "", "obra": "", "contato": "", "responsavel": ""}

# --- BARRA LATERAL ---
st.sidebar.header("👤 Informações")
st.session_state.cliente["responsavel"] = st.sidebar.text_input("Seu Nome (Responsável)", value=st.session_state.cliente["responsavel"], placeholder="Ex: João Pedreiro")
st.sidebar.markdown("---")
st.session_state.cliente["nome"] = st.sidebar.text_input("Nome do Cliente", value=st.session_state.cliente["nome"])
st.session_state.cliente["obra"] = st.sidebar.text_input("Endereço da Obra", value=st.session_state.cliente["obra"])
st.session_state.cliente["contato"] = st.sidebar.text_input("Contato (Telefone)", value=st.session_state.cliente["contato"])

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.servicos = pd.DataFrame(columns=["Descrição", "Valor (R$)", "Status"])
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Medidas", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)"])
    st.session_state.cliente = {"nome": "", "obra": "", "contato": "", "responsavel": ""}
    st.rerun()

st.title(f"📄 Orçamento: {st.session_state.cliente['nome']}")

tab1, tab2, tab3 = st.tabs(["⚒️ Mão de Obra", "🧱 Materiais", "💾 Gerar Orçamento"])

# --- ABA 1: MÃO DE OBRA ---
with tab1:
    st.header("Serviços do Pedreiro")
    with st.form("form_servico", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        desc_serv = col1.text_input("Descrição do Serviço")
        val_serv = col2.number_input("Valor Inicial (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            if desc_serv:
                texto_limpo = corrigir_texto(desc_serv)
                novo = pd.DataFrame([{"Descrição": texto_limpo, "Valor (R$)": val_serv, "Status": "Pendente"}])
                st.session_state.servicos = pd.concat([st.session_state.servicos, novo], ignore_index=True)
                st.rerun()
    
    if not st.session_state.servicos.empty:
        for index, row in st.session_state.servicos.iterrows():
            with st.expander(f"⚙️ {row['Descrição']} - R$ {row['Valor (R$)']:,.2f}"):
                c1, c2, c3 = st.columns([2, 1, 1])
                novo_valor = c1.number_input(f"Editar Valor", value=float(row["Valor (R$)"]), key=f"edit_val_{index}")
                if c2.button("Salvar", key=f"save_{index}"):
                    st.session_state.servicos.at[index, "Valor (R$)"] = novo_valor
                    st.rerun()
                status_label = "Concluir" if row["Status"] == "Pendente" else "Reabrir"
                if c3.button(status_label, key=f"status_{index}"):
                    st.session_state.servicos.at[index, "Status"] = "Concluído" if row["Status"] == "Pendente" else "Pendente"
                    st.rerun()
    total_mao = st.session_state.servicos["Valor (R$)"].sum()

# --- ABA 2: MATERIAIS ---
with tab2:
    st.header("Lista de Materiais")
    with st.form("form_mat", clear_on_submit=True):
        col_m1, col_m2 = st.columns([2, 1])
        it = col_m1.text_input("Material")
        med = col_m2.text_input("Medida")
        c1, c2, c3 = st.columns([1, 1, 2])
        qt = c1.number_input("Qtd", min_value=0.0)
        un = c2.selectbox("Unid.", ["Rolos", "Un", "Metros", "Sacos", "m²", "Pecas", "Latas", "Kg"])
        pr = c3.number_input("Preço Unit. (R$)", min_value=0.0)
        if st.form_submit_button("Incluir Material"):
            if it:
                it_corrigido = corrigir_texto(it)
                novo_m = pd.DataFrame([{"Item": it_corrigido, "Medidas": med, "Quantidade": qt, "Unidade": un, "Preço Unit. (R$)": pr, "Total (R$)": qt*pr}])
                st.session_state.materiais = pd.concat([st.session_state.materiais, novo_m], ignore_index=True)
                st.rerun()
    st.dataframe(st.session_state.materiais, use_container_width=True)
    total_mat = st.session_state.materiais["Total (R$)"].sum()

# --- ABA 3: PDF PROFISSIONAL ---
with tab3:
    st.header("Finalizar Orçamento")
    total_geral = total_mao + total_mat
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Mão de Obra", f"R$ {total_mao:,.2f}")
    col_res2.metric("Materiais", f"R$ {total_mat:,.2f}")
    
    if st.button("Gerar PDF Profissional"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(190, 10, "ORÇAMENTO DE OBRA", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Helvetica", '', 11)
        pdf.cell(190, 7, f"Responsável: {st.session_state.cliente['responsavel']}", ln=True)
        pdf.cell(190, 7, f"Cliente: {st.session_state.cliente['nome']}", ln=True)
        pdf.cell(190, 7, f"Contato: {st.session_state.cliente['contato']}", ln=True)
        pdf.cell(190, 7, f"Local: {st.session_state.cliente['obra']}", ln=True)
        pdf.cell(190, 7, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(10)

        # MÃO DE OBRA
        pdf.set_fill_color(235, 235, 235)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, " 1. DETALHAMENTO DE MÃO DE OBRA", ln=True, fill=True)
        pdf.set_font("Helvetica", '', 10)
        for _, r in st.session_state.servicos.iterrows():
            status = "[OK]" if r["Status"] == "Concluído" else "[ ]"
            pdf.cell(150, 8, f"{status} {r['Descrição']}", border='B')
            pdf.cell(40, 8, f"R$ {r['Valor (R$)']:,.2f}", border='B', ln=True, align='R')
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(190, 10, f"TOTAL MÃO DE OBRA: R$ {total_mao:,.2f}", ln=True, align='R')
        pdf.ln(5)

        # MATERIAIS
        pdf.set_fill_color(235, 235, 235)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, " 2. DETALHAMENTO DE MATERIAIS", ln=True, fill=True)
        pdf.set_font("Helvetica", '', 9)
        for _, r in st.session_state.materiais.iterrows():
            txt = f"- {r['Item']} ({r['Medidas']}): {r['Quantidade']} {r['Unidade']} x R$ {r['Preço Unit. (R$)']:,.2f}"
            pdf.cell(150, 7, txt, border='B')
            pdf.cell(40, 7, f"R$ {r['Total (R$)']:,.2f}", border='B', ln=True, align='R')
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(190, 10, f"TOTAL MATERIAIS: R$ {total_mat:,.2f}", ln=True, align='R')
        
        # TOTAL GERAL
        pdf.ln(10)
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(190, 12, f"VALOR TOTAL DA OBRA: R$ {total_geral:,.2f}", border=1, ln=True, align='C')

        # RODAPÉ E ASSINATURAS
        pdf.ln(25)
        pdf.line(20, pdf.get_y(), 85, pdf.get_y())
        pdf.line(105, pdf.get_y(), 170, pdf.get_y())
        pdf.set_font("Helvetica", 'B', 9)
        pdf.cell(85, 5, f"{st.session_state.cliente['responsavel']}", align='C')
        pdf.cell(105, 5, f"{st.session_state.cliente['nome']}", align='C')
        pdf.ln(4)
        pdf.set_font("Helvetica", '', 8)
        pdf.cell(85, 5, "(Responsável Técnico)", align='C')
        pdf.cell(105, 5, "(Cliente)", align='C')
        
        pdf.output("orcamento.pdf")
        with open("orcamento.pdf", "rb") as f:
            st.download_button("📥 Baixar PDF com Assinatura", f, "orcamento.pdf")
