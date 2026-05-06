import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# Configuração da página
st.set_page_config(page_title="Orçamentista Pro", layout="wide")

# --- FUNÇÃO DE CORREÇÃO DE ESCRITA ---
def corrigir_texto(texto):
    if not texto:
        return ""
    # Remove espaços inúteis e coloca a primeira letra em maiúsculo
    texto = texto.strip().capitalize()
    
    # Dicionário de correções rápidas para erros comuns de obra
    correcoes = {
        "Cimento": ["cimento", "cimeto", "simento"],
        "Treliça": ["trelica", "treliça", "terliça"],
        "Argamassa": ["argamassa", "argamassa", "algamassa"],
        "Elétrica": ["eletrica", "eletrica"],
        "Hidráulica": ["hidraulica", "idraulica"],
        "Vergalhão": ["vergalhao", "vergalhao"],
        "Concluído": ["concluido", "concluido"],
        "Pendente": ["pedente", "pendente"]
    }
    
    for correto, errados in correcoes.items():
        for errado in errados:
            if texto.lower() == errado:
                return correto
    return texto

# --- INICIALIZAÇÃO DE DADOS ---
if 'servicos' not in st.session_state:
    st.session_state.servicos = pd.DataFrame(columns=["Descrição", "Valor (R$)", "Status"])
if 'materiais' not in st.session_state:
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Medidas", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)"])
if 'cliente' not in st.session_state:
    st.session_state.cliente = {"nome": "", "obra": "", "contato": ""}

# --- BARRA LATERAL ---
st.sidebar.header("👤 Dados do Cliente")
st.session_state.cliente["nome"] = st.sidebar.text_input("Nome do Cliente", value=st.session_state.cliente["nome"])
st.session_state.cliente["obra"] = st.sidebar.text_input("Endereço da Obra", value=st.session_state.cliente["obra"])
st.session_state.cliente["contato"] = st.sidebar.text_input("Contato (Telefone)", value=st.session_state.cliente["contato"])

if st.sidebar.button("🧹 LIMPAR TUDO"):
    st.session_state.servicos = pd.DataFrame(columns=["Descrição", "Valor (R$)", "Status"])
    st.session_state.materiais = pd.DataFrame(columns=["Item", "Medidas", "Quantidade", "Unidade", "Preço Unit. (R$)", "Total (R$)"])
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
                # Aplica o corretor antes de salvar
                texto_limpo = corrigir_texto(desc_serv)
                novo = pd.DataFrame([{"Descrição": texto_limpo, "Valor (R$)": val_serv, "Status": "Pendente"}])
                st.session_state.servicos = pd.concat([st.session_state.servicos, novo], ignore_index=True)
                st.rerun()
    
    if not st.session_state.servicos.empty:
        for index, row in st.session_state.servicos.iterrows():
            col_d, col_v, col_s, col_b = st.columns([3, 1, 1, 1])
            col_d.write(row["Descrição"])
            col_v.write(f"R$ {row['Valor (R$)']:,.2f}")
            status_cor = "🔴" if row["Status"] == "Pendente" else "🟢"
            col_s.write(f"{status_cor} {row['Status']}")
            if col_b.button("Status", key=f"btn_{index}"):
                st.session_state.servicos.at[index, "Status"] = "Concluído" if row["Status"] == "Pendente" else "Pendente"
                st.rerun()

# --- ABA 2: MATERIAIS ---
with tab2:
    st.header("Lista de Materiais")
    with st.form("form_mat", clear_on_submit=True):
        col_m1, col_m2 = st.columns([2, 1])
        it = col_m1.text_input("Material")
        med = col_m2.text_input("Medida")
        
        c1, c2, c3 = st.columns([1, 1, 2])
        qt = c1.number_input("Qtd", min_value=0.0)
        un = c2.selectbox("Unid.", ["Rolos", "Un", "Metros", "Sacos", "m²", "Pecas", "Latas", "Kg", "Pares"])
        pr = c3.number_input("Preço Unit. (R$)", min_value=0.0)
        
        if st.form_submit_button("Incluir Material"):
            if it:
                # Aplica o corretor no material e na medida
                it_corrigido = corrigir_texto(it)
                total_it = qt * pr
                novo_m = pd.DataFrame([{"Item": it_corrigido, "Medidas": med, "Quantidade": qt, "Unidade": un, "Preço Unit. (R$)": pr, "Total (R$)": total_it}])
                st.session_state.materiais = pd.concat([st.session_state.materiais, novo_m], ignore_index=True)
                st.rerun()

    st.dataframe(st.session_state.materiais, use_container_width=True)

# --- ABA 3: PDF ---
with tab3:
    st.header("Finalizar Orçamento")
    total_mao = st.session_state.servicos["Valor (R$)"].sum()
    total_mat = st.session_state.materiais["Total (R$)"].sum()
    total_geral = total_mao + total_mat
    st.subheader(f"Total Geral: R$ {total_geral:,.2f}")
    
    if st.button("Gerar PDF Completo"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(190, 10, "ORCAMENTO DE OBRA", ln=True, align='C')
        
        pdf.set_font("Helvetica", '', 11)
        pdf.ln(5)
        pdf.cell(190, 7, f"Cliente: {st.session_state.cliente['nome']}", ln=True)
        pdf.cell(190, 7, f"Endereco: {st.session_state.cliente['obra']}", ln=True)
        pdf.cell(190, 7, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
        pdf.ln(10)

        # Seção Mão de Obra
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, "1. MAO DE OBRA", ln=True)
        pdf.set_font("Helvetica", '', 10)
        for _, r in st.session_state.servicos.iterrows():
            pdf.cell(150, 8, f"- {r['Descrição']}", border='B')
            pdf.cell(40, 8, f"R$ {r['Valor (R$)']:,.2f}", border='B', ln=True, align='R')
        
        pdf.ln(5)
        # Seção Materiais
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(190, 10, "2. MATERIAIS", ln=True)
        pdf.set_font("Helvetica", '', 9)
        for _, r in st.session_state.materiais.iterrows():
            pdf.cell(190, 7, f"- {r['Item']} ({r['Medidas']}): {r['Quantidade']} {r['Unidade']} - R$ {r['Total (R$)']:,.2f}", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(190, 10, f"TOTAL: R$ {total_geral:,.2f}", ln=True, align='R')
        
        pdf.ln(25)
        pdf.line(20, pdf.get_y(), 85, pdf.get_y())
        pdf.line(105, pdf.get_y(), 170, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", '', 10)
        pdf.cell(85, 5, "Assinatura Pedreiro", align='C')
        pdf.cell(105, 5, "Assinatura Cliente", align='C')
        
        pdf.output("orcamento.pdf")
        with open("orcamento.pdf", "rb") as f:
            st.download_button("📥 Baixar PDF", f, "orcamento.pdf")
